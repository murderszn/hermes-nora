#!/usr/bin/env python3
"""
HERMES :: Agent Control Dashboard — local telemetry server.

Aggregates live Hermes activity from the gateway state, logs, Discord channel
directory and agent telemetry, and serves a JARVIS-style HTML dashboard.

Stdlib only. Run it, then open http://127.0.0.1:7878
"""
import ctypes
import json
import os
import re
import socket
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import queue

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

INBOUND_RE = re.compile(r"inbound message: platform=(\w+) user=(\S+) chat=(\S+) msg=(.*)$")
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


def parse_channels():
    cj = load_json(CHANNEL_DIR)
    disc = (cj.get("platforms") or {}).get("discord") or []
    by_type = {}
    items = []
    log_map = {}  # track events from richer gateway parse if we add it
    for ch in disc:
        t = ch.get("type", "?")
        by_type[t] = by_type.get(t, 0) + 1
        name = ch.get("name", "")
        guild = ch.get("guild", "")
        cid = ch.get("id", "")
        topic = ""
        parent = ""
        # thread names like ".../#general / prompt / topic 123"
        if t == "thread" and "/" in name:
            parts = [p.strip() for p in name.split("/")]
            if len(parts) >= 3:
                parent = parts[1] if parts[1].startswith("#") else ""
                # prompt is usually parts[2]
                topic = parts[2] if len(parts) > 2 else ""
            else:
                topic = name
            # drop leading/trailing repeated topic ids
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
        })
    return {"by_type": by_type, "total": len(disc), "items": items[:20],
            "updated": cj.get("updated_at"), "log_map": log_map}


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
                with open(os.path.join(HERE, "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            elif path == "/api/state":
                self._send(200, json.dumps(build_state()).encode("utf-8"))
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
    print("  HERMES :: Agent Control Dashboard")
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
