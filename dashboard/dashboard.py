#!/usr/bin/env python3
"""
HERMES :: Agent Control Dashboard — local telemetry server.

Aggregates live Hermes activity from the gateway state, logs, Discord channel
directory and agent telemetry, and serves a JARVIS-style HTML dashboard.

Stdlib only. Run it, then open http://127.0.0.1:7878
"""
import ctypes
import functools
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import queue


def ttl_cache(seconds):
    """Memoize a zero-arg function for `seconds`, thread-safe.

    Keeps the last good value if a refresh raises, so transient subprocess
    failures don't blank out the dashboard.
    """
    def deco(fn):
        store = {"t": 0.0, "v": None, "has": False}
        lock = threading.Lock()

        @functools.wraps(fn)
        def wrapper():
            now = time.time()
            with lock:
                if store["has"] and now - store["t"] < seconds:
                    return store["v"]
            try:
                val = fn()
            except Exception:
                with lock:
                    if store["has"]:
                        return store["v"]
                raise
            with lock:
                store.update(t=now, v=val, has=True)
            return val
        return wrapper
    return deco

PORT = 7878
HERE = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = r"C:\Users\jjohn\AppData\Local\hermes"
ASSET_DIR = r"C:\Users\jjohn\OneDrive\Desktop\hermes"
LOGS = os.path.join(DATA_DIR, "logs")

GATEWAY_STATE = os.path.join(DATA_DIR, "gateway_state.json")
CHANNEL_DIR = os.path.join(DATA_DIR, "channel_directory.json")
GATEWAY_LOG = os.path.join(LOGS, "gateway.log")
AGENT_LOG = os.path.join(LOGS, "agent.log")
ERRORS_LOG = os.path.join(LOGS, "errors.log")
WATCHDOG_LOG = os.path.join(LOGS, "gateway-watchdog.log")

ASSETS = {
    "wallpaper": (os.path.join(ASSET_DIR, "hermes-wallpaper.jfif"), "image/jpeg"),
    "logo": (os.path.join(ASSET_DIR, "hermes-logo.PNG"), "image/png"),
    "video": (os.path.join(ASSET_DIR, "lumen-kaleid-3509.webm"), "video/webm"),
    "avatar-nora": (os.path.join(ASSET_DIR, "avatar-nora-hermes-nora.png"), "image/png"),
    "avatar-murderszn": (os.path.join(ASSET_DIR, "avatar-murderszn.png"), "image/png"),
}

TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")

# ---------------------------------------------------------------- helpers

def today():
    return datetime.now().strftime("%Y-%m-%d")


def read_tail(path, max_bytes=220_000):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - max_bytes))
            return f.read().decode("utf-8", errors="replace")
    except FileNotFoundError:
        return ""
    except OSError:
        return ""


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except Exception:
        return {}


def pid_alive(pid):
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    k = ctypes.windll.kernel32
    h = k.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = k.GetExitCodeProcess(h, ctypes.byref(code))
    k.CloseHandle(h)
    return bool(ok) and code.value == STILL_ACTIVE


_proc_cache = {"t": 0.0, "running": False, "pid": None}


def gateway_running():
    """True if a `python ... gateway run` process is alive. Cached ~8s."""
    now = time.time()
    if now - _proc_cache["t"] < 8:
        return _proc_cache["running"], _proc_cache["pid"]
    running, pid = False, None
    try:
        out = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'", "get",
             "ProcessId,CommandLine", "/format:list"],
            capture_output=True, text=True, timeout=8,
        ).stdout
        block_cmd, block_pid = None, None
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("CommandLine="):
                block_cmd = line[len("CommandLine="):]
            elif line.startswith("ProcessId="):
                block_pid = line[len("ProcessId="):]
                if block_cmd and "gateway" in block_cmd.lower() and re.search(r"\brun\b", block_cmd.lower()):
                    running, pid = True, block_pid
                block_cmd = None
    except Exception:
        # fall back to state-file pid liveness
        st = load_json(GATEWAY_STATE)
        if pid_alive(st.get("pid")):
            running, pid = True, str(st.get("pid"))
    _proc_cache.update(t=now, running=running, pid=pid)
    return running, pid


def humanize_ago(dt):
    secs = (datetime.now() - dt).total_seconds()
    if secs < 0:
        secs = 0
    if secs < 60:
        return f"{int(secs)}s ago"
    if secs < 3600:
        return f"{int(secs // 60)}m ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    return f"{int(secs // 86400)}d ago"


def parse_ts(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

# ---------------------------------------------------------------- parsers

INBOUND_RE = re.compile(r"inbound message: platform=(\w+) user=(.+?) chat=(\S+) msg=(.*)$")
RESP_RE = re.compile(r"response ready: platform=(\w+) chat=(\S+) time=([\d.]+)s api_calls=(\d+) response=(\d+) chars")
CONNAS_RE = re.compile(r"Connected as (\S+)")
SEND_RE = re.compile(r"\[Discord\] Sending response \((\d+) chars\)")
EVICT_RE = re.compile(r"evicted (\d+) agent")


def parse_gateway_log():
    txt = read_tail(GATEWAY_LOG)
    lines = txt.splitlines()
    td = today()
    bot = None
    events = []
    channel_events = {}
    msgs_today = 0
    resp_times = []
    last_resp = None
    last_event_ts = None
    for ln in lines:
        m = TS_RE.match(ln)
        ts = m.group(1) if m else None
        if ts:
            last_event_ts = ts
        c = CONNAS_RE.search(ln)
        if c:
            bot = c.group(1)
        mi = INBOUND_RE.search(ln)
        if mi:
            plat, user, chat, msg = mi.groups()
            msg = msg.strip().strip("'")
            if ts and ts.startswith(td):
                msgs_today += 1
            events.append({"ts": ts, "type": "in", "user": user,
                           "text": msg[:160], "chat": chat})
            channel_events.setdefault(chat, []).append({"ts": ts, "type": "in", "user": user, "text": msg[:160]})
            continue
        mr = RESP_RE.search(ln)
        if mr:
            plat, chat, t, api, chars = mr.groups()
            last_resp = {"time": float(t), "api_calls": int(api), "chars": int(chars)}
            if ts and ts.startswith(td):
                resp_times.append(float(t))
            events.append({"ts": ts, "type": "out",
                           "text": f"replied · {chars} chars · {t}s · {api} api calls",
                           "chat": chat})
            channel_events.setdefault(chat, []).append({"ts": ts, "type": "out", "user": "hermes",
               "text": f"replied · {chars} chars · {t}s · {api} api calls"})
            continue
        if "Starting Hermes Gateway" in ln:
            events.append({"ts": ts, "type": "sys", "text": "gateway started"})
        elif "discord connected" in ln.lower():
            events.append({"ts": ts, "type": "sys", "text": "discord uplink established"})
        elif EVICT_RE.search(ln):
            n = EVICT_RE.search(ln).group(1)
            events.append({"ts": ts, "type": "sys", "text": f"idle sweep · {n} session(s) evicted"})
    avg = round(sum(resp_times) / len(resp_times), 1) if resp_times else None
    # sort each channel newest-first and keep last 25
    for chat_id in channel_events:
        channel_events[chat_id].sort(key=lambda e: e.get("ts") or "", reverse=True)
        channel_events[chat_id] = channel_events[chat_id][:25]

    return {
        "bot": bot,
        "events": events[-60:],
        "msgs_today": msgs_today,
        "avg_response": avg,
        "responses_today": len(resp_times),
        "last_response": last_resp,
        "last_event": last_event_ts,
        "channel_events": channel_events,
    }


API_RE = re.compile(r"API call #(\d+): model=(\S+) provider=(\S+) in=(\d+) out=(\d+) total=(\d+) latency=([\d.]+)s")
TOOL_RE = re.compile(r"tool (\w+) (completed|failed) \(([\d.]+)s")


def parse_agent_log():
    txt = read_tail(AGENT_LOG)
    td = today()
    model = provider = None
    tokens_today = 0
    api_today = 0
    latencies = []
    tools = []
    events = []
    for ln in txt.splitlines():
        m = TS_RE.match(ln)
        ts = m.group(1) if m else None
        a = API_RE.search(ln)
        if a:
            _, model, provider, _in, out, total, lat = a.groups()
            if ts and ts.startswith(td):
                tokens_today += int(total)
                api_today += 1
                latencies.append(float(lat))
            continue
        t = TOOL_RE.search(ln)
        if t:
            name, status, dur = t.groups()
            tools.append({"ts": ts, "name": name, "status": status, "dur": float(dur)})
            events.append({"ts": ts, "type": "tool",
                           "text": f"tool {name} {status} ({dur}s)"})
    avg_lat = round(sum(latencies) / len(latencies), 1) if latencies else None
    return {
        "model": model,
        "provider": provider,
        "tokens_today": tokens_today,
        "api_today": api_today,
        "avg_latency": avg_lat,
        "recent_tools": tools[-12:],
        "events": events[-30:],
    }


FAH_WORK = r"C:\ProgramData\FAHClient\work"

def _parse_wuinfo(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        # first 4 bytes = length, rest = ascii payload
        ln = int.from_bytes(data[:4], "little")
        payload = data[4:4 + ln].decode("utf-8", errors="replace")
    except Exception:
        return {}
    # payload looks like "Core27 p1824 6" or "Gromacs p18806"
    core = ""
    project = ""
    slot = ""
    m = re.search(r"Core\s*(\d+)", payload)
    if m:
        core = m.group(1)
    m = re.search(r"p(\d+)", payload)
    if m:
        project = m.group(1)
    # slot from file suffix? filename is wuinfo_01.dat
    m = re.search(r"wuinfo_(\d+)\.dat$", path)
    if m:
        slot = m.group(1)
    info = {"core": core, "project": project, "slot": slot}
    # parse counts after the string
    rest = data[4 + ln:]
    # keep device id if present
    if len(rest) >= 8:
        info["device"] = int.from_bytes(rest[4:8], "little")
    return info


def parse_fah():
    try:
        units = []
        for name in os.listdir(FAH_WORK):
            wdir = os.path.join(FAH_WORK, name)
            if not os.path.isdir(wdir):
                continue
            wuinfo = os.path.join(wdir, "wuinfo_01.dat")
            logfile = os.path.join(wdir, "logfile_01.txt")
            info = _parse_wuinfo(wuinfo) if os.path.exists(wuinfo) else {}
            progress = ""
            total_steps = ""
            completed_steps = ""
            if os.path.exists(logfile):
                try:
                    with open(logfile, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                    for line in lines:
                        m = re.search(r"Completed\s+(\d+)\s+out\s+of\s+(\d+)\s+steps\s+\((\d+)%\)", line)
                        if m:
                            completed_steps = m.group(1)
                            total_steps = m.group(2)
                            progress = m.group(3) + "%"
                except Exception:
                    pass
            status = "progressing"
            if os.path.exists(logfile):
                try:
                    tail = ""
                    with open(logfile, "r", encoding="utf-8", errors="replace") as f:
                        tail = f.readlines()[-5:]
                    if any("INTERRUPTED" in l or "Core Shutdown" in l for l in tail):
                        status = "interrupted"
                except Exception:
                    pass
            units.append({
                "id": name,
                "core": info.get("core", ""),
                "project": info.get("project", ""),
                "slot": info.get("slot", ""),
                "device": info.get("device"),
                "progress": progress,
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "status": status,
            })
        units.sort(key=lambda u: int(u.get("project") or 0), reverse=True)
        return units[:8]
    except Exception:
        return []


def parse_unified_messages(chans, msgs_by_id):
    flat = []
    for ch in chans:
        cid = ch.get("id", "")
        msgs = msgs_by_id.get(cid, [])
        for m in msgs:
            flat.append({
                "ts": m.get("ts") or "",
                "type": m.get("type", "in"),
                "user": m.get("user", ""),
                "text": m.get("text", ""),
                "source": ch.get("platform", "discord"),
                "channel_id": cid,
                "channel_name": ch.get("name", cid),
            })
    flat.sort(key=lambda x: x.get("ts") or "", reverse=True)
    return flat[:120]


ERR_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} [\d:,]+)\s+(WARNING|ERROR|CRITICAL)\b\s*(?:\[[^\]]*\])?\s*([\w.]+)?:?\s*(.*)$")


def parse_errors():
    txt = read_tail(ERRORS_LOG, 120_000)
    td = today()
    recent = []
    count_today = 0
    for ln in txt.splitlines():
        m = ERR_RE.match(ln)
        if not m:
            continue
        ts, level, logger, msg = m.groups()
        if ts.startswith(td):
            count_today += 1
        recent.append({"ts": ts, "level": level, "logger": logger or "",
                       "text": (msg or "")[:180]})
    return {"count_today": count_today, "recent": recent[-12:]}


def parse_watchdog():
    txt = read_tail(WATCHDOG_LOG, 40_000)
    restarts = 0
    last = None
    for ln in txt.splitlines():
        if "started it" in ln.lower():
            restarts += 1
            m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", ln)
            if m:
                last = m.group(1)
    return {"restarts": restarts, "last_restart": last}


def parse_moltbook_activity():
    path = os.path.expanduser("~/.config/moltbook/engagement_activity.jsonl")
    items = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    obj["ts"] = obj.get("ts", "")
                    items.append(obj)
                except Exception:
                    continue
    except Exception:
        pass
    items.sort(key=lambda x: x.get("ts") or "", reverse=True)
    return items[:60]


def parse_channels():
    cj = load_json(CHANNEL_DIR)
    platforms = (cj.get("platforms") or {})
    disc = (platforms.get("discord") or [])
    email = (platforms.get("email") or [])
    by_type = {}
    items = []
    log_map = {}
    for ch in disc:
        t = ch.get("type", "?")
        by_type[t] = by_type.get(t, 0) + 1
        name = ch.get("name", "")
        guild = ch.get("guild", "")
        cid = ch.get("id", "")
        topic = ""
        parent = ""
        if t == "thread" and "/" in name:
            parts = [p.strip() for p in name.split("/")]
            if len(parts) >= 3:
                parent = parts[1] if parts[1].startswith("#") else ""
                topic = parts[2] if len(parts) > 2 else ""
            else:
                topic = name
            topic = re.sub(r"(/topic\s*[\w:]+)+$", "", topic, flags=re.I).strip()
            display = topic[:80] if topic else name[:80]
        else:
            display = name[:70]
        items.append({
            "id": cid,
            "type": t,
            "name": display,
            "guild": guild,
            "parent": parent,
            "topic": topic,
            "last_ts": "",
            "preview": "",
            "platform": "discord",
        })
    for ch in email:
        t = ch.get("type", "dm")
        by_type[t] = by_type.get(t, 0) + 1
        cid = ch.get("id", "")
        display = ch.get("name", cid)
        items.append({
            "id": cid,
            "type": t,
            "name": display,
            "guild": "",
            "parent": "",
            "topic": "",
            "last_ts": "",
            "preview": "",
            "platform": "email",
        })
    return {"by_type": by_type, "total": len(items), "items": items,
            "updated": cj.get("updated_at"), "log_map": log_map}


@ttl_cache(30)  # scheduled-task status barely changes; schtasks spawn is slow
def watchdog_task_state():
    try:
        out = subprocess.run(
            ["schtasks", "/Query", "/TN", "HermesGatewayWatchdog", "/FO", "LIST"],
            capture_output=True, text=True, timeout=6).stdout
        status = re.search(r"Status:\s*(.+)", out)
        nextrun = re.search(r"Next Run Time:\s*(.+)", out)
        return {"present": "HermesGatewayWatchdog" in out,
                "status": (status.group(1).strip() if status else "?"),
                "next_run": (nextrun.group(1).strip() if nextrun else "?")}
    except Exception:
        return {"present": False, "status": "?", "next_run": "?"}


# ---------------------------------------------------------------- system stats

@ttl_cache(4)
def get_cpu_usage():
    try:
        out = subprocess.run(
            ["wmic", "cpu", "get", "loadpercentage", "/format:list"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        for line in out.splitlines():
            if "=" in line:
                _, val = line.split("=", 1)
                if val.strip().isdigit():
                    return int(val.strip())
    except Exception:
        pass
    return None


@ttl_cache(4)
def get_gpu_usage():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        if not out:
            return None
        parts = [p.strip() for p in out.split(",")]
        return {
            "usage": int(parts[0]) if parts[0].isdigit() else None,
            "mem_used": int(parts[1]) if parts[1].isdigit() else None,
            "mem_total": int(parts[2]) if parts[2].isdigit() else None,
            "temp": int(parts[3]) if parts[3].isdigit() else None,
        }
    except Exception:
        return None


@ttl_cache(4)
def get_ram_usage():
    try:
        out = subprocess.run(
            ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/format:list"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        vals = {}
        for line in out.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = int(v.strip()) if v.strip().isdigit() else 0
        total = vals.get("TotalVisibleMemorySize", 0)
        free = vals.get("FreePhysicalMemory", 0)
        if total:
            return {
                "total_mb": round(total / 1024),
                "used_mb": round((total - free) / 1024),
                "pct": round((total - free) * 100 / total),
            }
    except Exception:
        pass
    return None


def get_disk_usage(path="C:\\"):
    try:
        usage = shutil.disk_usage(path)
        label = path.rstrip("\\").rstrip("/").upper()
        return {
            "pct": round(usage.used * 100 / usage.total) if usage.total else 0,
            "label": label,
            "used_gb": round(usage.used / (1024**3)),
            "total_gb": round(usage.total / (1024**3)),
        }
    except Exception:
        pass
    return None


@ttl_cache(4)
def get_all_disks():
    drives = []
    for prefix in ("C", "D", "G"):
        d = get_disk_usage(f"{prefix}:\\")
        if d:
            drives.append(d)
    return drives


def _ps(cmd):
    try:
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False).stdout.strip()
        return out
    except Exception:
        return ""


@ttl_cache(600)  # static inventory (CPU/GPU names, RAM part #s, disk models) — never changes
def get_hardware_detail():
    try:
        cpu = _ps("powershell -NoProfile -Command \"(Get-CimInstance Win32_Processor).Name\"")
        gpu_raw = _ps("powershell -NoProfile -Command \"Get-CimInstance Win32_VideoController | Select-Object -Expand Name\"")
        gpus = [x.strip() for x in gpu_raw.splitlines() if x.strip()] if gpu_raw else []
        ram_raw = _ps("powershell -NoProfile -Command \"Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, PartNumber, SerialNumber, Capacity | ConvertTo-Json\"")
        ram = []
        try:
            ram = json.loads(ram_raw)
            if isinstance(ram, dict):
                ram = [ram]
        except Exception:
            ram = []
        disk_raw = _ps("powershell -NoProfile -Command \"Get-CimInstance Win32_DiskDrive | Select-Object Model, Size, InterfaceType, MediaType | ConvertTo-Json\"")
        disks = []
        try:
            disks = json.loads(disk_raw)
            if isinstance(disks, dict):
                disks = [disks]
        except Exception:
            disks = []
        return {
            "cpu": cpu,
            "gpus": gpus,
            "ram": ram,
            "disks": disks,
        }
    except Exception:
        return {}


# ---------------------------------------------------------------- aggregate

def build_state():
    running, pid = gateway_running()
    gw = load_json(GATEWAY_STATE)
    glog = parse_gateway_log()
    alog = parse_agent_log()
    errs = parse_errors()
    wd = parse_watchdog()
    chans = parse_channels()
    task = watchdog_task_state()
    molt = parse_moltbook_activity()
    fah = parse_fah()

    # map canonical channel ids (from channel_dir) to log chat keys
    ch_key_map = {}
    for c in chans["items"]:
        cid = c.get("id", "")
        if not cid:
            continue
        ch_key_map[cid] = cid
        if ":" in cid:
            ch_key_map[cid.split(":")[-1]] = cid

    # merge log key -> canonical channel id so frontend can look up by c.id
    raw_msgs = glog.get("channel_events", {})
    msgs_by_id = {}
    for log_key, msgs in raw_msgs.items():
        msgs_by_id[log_key] = msgs
        ch_id = ch_key_map.get(log_key)
        if ch_id and ch_id != log_key:
            msgs_by_id[ch_id] = msgs

    # enrich channel metadata with latest message timestamp + preview
    for ch in chans.get("items", []):
        cid = ch.get("id", "")
        msgs = msgs_by_id.get(cid, [])
        if msgs:
            ch["last_ts"] = msgs[0].get("ts", "")
            # preview prefers actual user text over outbound "replied" summaries
            for m in msgs:
                if (m.get("type") or "") == "in":
                    txt = (m.get("text") or "").strip()
                    if txt:
                        ch["preview"] = txt[:80]
                        break

    disc_state = (((gw.get("platforms") or {}).get("discord") or {}).get("state"))

    # merge activity feed
    feed = list(glog["events"]) + list(alog["events"])
    feed = [e for e in feed if e.get("ts")]
    feed.sort(key=lambda e: e["ts"], reverse=True)
    feed = feed[:45]

    last_evt = glog["last_event"]
    last_ago = None
    if last_evt:
        dt = parse_ts(last_evt)
        if dt:
            last_ago = humanize_ago(dt)

    unified = parse_unified_messages(chans["items"], msgs_by_id)

    return {
        "server_time": datetime.now().strftime("%H:%M:%S"),
        "server_date": datetime.now().strftime("%a %d %b %Y"),
        "system": {
            "gateway_online": running,
            "gateway_pid": pid or gw.get("pid"),
            "gateway_state": gw.get("gateway_state", "unknown"),
            "active_agents": gw.get("active_agents", 0),
            "last_activity": last_ago,
        },
        "discord": {
            "bot": glog["bot"],
            "state": disc_state or ("connected" if running else "offline"),
            "msgs_today": glog["msgs_today"],
            "responses_today": glog["responses_today"],
            "avg_response": glog["avg_response"],
            "last_response": glog["last_response"],
        },
        "channels": {
            **chans,
            "messages_by_id": msgs_by_id,
        },
        "agent": alog,
        "errors": errs,
        "watchdog": {**wd, "task": task},
        "activity": feed,
        "moltbook": {"activity": molt},
        "fah": fah,
        "unified_messages": unified,
        "hardware_detail": get_hardware_detail(),
        "avatars": {
            "nora": "/assets/avatar-nora",
            "murderszn": "/assets/avatar-murderszn",
        },
        "hardware": {
            "cpu": get_cpu_usage(),
            "gpu": get_gpu_usage(),
            "ram": get_ram_usage(),
            "disks": get_all_disks(),
        },
    }


# ---------------------------------------------------------------- http

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json", cache=False):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if not cache:
            self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        try:
            if path == "/" or path == "/index.html":
                body = open(os.path.join(HERE, "index.html"), "rb").read()
                self._send(200, body, "text/html; charset=utf-8", cache=False)
            elif path == "/api/state":
                self._send(200, json.dumps(build_state()).encode("utf-8"))
            elif path == "/api/logs/activity":
                state = build_state()
                lines = []
                for e in state.get("activity", []):
                    who = "nora" if e.get("type") == "out" else (e.get("user") or "user")
                    ts = e.get("ts") or ""
                    lines.append(f"[{ts}] {who}: {e.get('text','')}")
                body = "\n".join(lines).encode("utf-8")
                self._send(200, body, "text/plain; charset=utf-8", cache=False)
            elif path == "/api/logs/diagnostics":
                try:
                    state = build_state()
                    lines = []
                    errs = state.get("errors") or {}
                    if isinstance(errs, dict):
                        for e in errs.get("recent", []):
                            ts = e.get("ts") or ""
                            lines.append(f"[{ts}] {e.get('level','')}: {e.get('text','')}")
                    elif isinstance(errs, list):
                        for e in errs:
                            if isinstance(e, dict):
                                lines.append(f"[{e.get('ts','')}] {e.get('level','')}: {e.get('text','')}")
                    body = "\n".join(lines).encode("utf-8")
                    self._send(200, body, "text/plain; charset=utf-8", cache=False)
                except Exception as e:
                    self._send(500, str(e).encode("utf-8"), "text/plain; charset=utf-8")
            elif path.startswith("/assets/"):
                key = path[len("/assets/"):]
                if key in ASSETS:
                    fp, ctype = ASSETS[key]
                    with open(fp, "rb") as f:
                        self._send(200, f.read(), ctype, cache=True)
                else:
                    self._send(404, b"not found", "text/plain")
            elif path == "/favicon.ico":
                self._send(204, b"")
            else:
                self._send(404, b"not found", "text/plain")
        except BrokenPipeError:
            pass
        except Exception as e:
            try:
                self._send(500, json.dumps({"error": str(e)}).encode(), )
            except Exception:
                pass

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            length = int(self.headers.get("Content-Length", 0))
        except Exception:
            length = 0
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8", errors="replace")) if length else {}
        except Exception:
            body = {}

        if path == "/api/voice":
            text = (body.get("text") or "").strip()
            channel = (body.get("channel") or "").strip()
            if not text:
                self._send(400, json.dumps({"error": "empty text"}).encode())
                return
            cmd = ["hermes", "chat", "-q", text]
            if channel:
                cmd += ["--resume", channel]
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=os.path.expanduser("~"),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=False,
                )
                self._send(202, json.dumps({"queued": True, "pid": proc.pid}).encode())
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}).encode())
        elif path == "/api/fah/pause":
            try:
                subprocess.run(["taskkill", "/F", "/IM", "FAHClient.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
                subprocess.Popen([r"C:\Program Files\FAHClient\FAHClient.exe", "--cpus", "0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
                self._send(202, json.dumps({"ok": True}).encode())
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}).encode())
        elif path == "/api/fah/unpause":
            try:
                subprocess.run(["taskkill", "/F", "/IM", "FAHClient.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
                subprocess.Popen([r"C:\Program Files\FAHClient\FAHClient.exe", "--cpus", "15"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
                self._send(202, json.dumps({"ok": True}).encode())
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}).encode())
        else:
            self._send(404, b"not found")


def port_open(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.4)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def main():
    no_browser = "--no-browser" in sys.argv
    url = f"http://127.0.0.1:{PORT}"

    # Already running (e.g. started at login)? Just surface it and exit.
    if port_open(PORT):
        print(f"Dashboard already running at {url}")
        if not no_browser:
            try:
                webbrowser.open(url)
            except Exception:
                pass
        return

    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("=" * 52)
    print("  HERMES — NORA :: Agent Control Dashboard")
    print(f"  Live at  {url}")
    print("  Press Ctrl+C to stop")
    print("=" * 52)
    if not no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        srv.shutdown()


if __name__ == "__main__":
    main()
