
const $=id=>document.getElementById(id);
function tick(){ $("clock").textContent=new Date().toLocaleTimeString('en-GB'); }
setInterval(tick,1000);tick();

// fullscreen
const fsBtn=$("fsBtn");
function toggleFs(){
  if(!document.fullscreenElement){ (document.documentElement.requestFullscreen||document.documentElement.webkitRequestFullscreen).call(document.documentElement); }
  else{ (document.exitFullscreen||document.webkitExitFullscreen).call(document); }
}
fsBtn.onclick=toggleFs;
document.addEventListener('keydown',e=>{ if(e.key==='f'||e.key==='F') toggleFs(); });
document.addEventListener('fullscreenchange',()=>{ fsBtn.textContent=document.fullscreenElement?'⛶ EXIT':'⛶ FULLSCREEN'; });

function setLive(ok){
  const l=$("live");
  if(ok){l.classList.remove("stale");$("livetxt").textContent="LIVE";}
  else{l.classList.add("stale");$("livetxt").textContent="RECONNECTING";}
}
function evIcon(t){return t==="in"?"▸":t==="out"?"◂":t==="tool"?"⚙":"●";}
function hm(ts){return ts?ts.slice(11,16):"";}
function esc(s){return (s==null?"":String(s)).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function fmt(n){return (n||0).toLocaleString();}

let selectedSource = 'all';

async function refresh(){
  let s;
  try{ s=await (await fetch('/api/state',{cache:'no-store'})).json(); }
  catch(e){ setLive(false); return; }
  setLive(true);
  $("date").textContent=s.server_date;

  const on=s.system.gateway_online;
  $("heroRight").textContent=(s.agent.model||"idle");

  $("kAgents").textContent=s.system.active_agents;
  $("kPid").textContent=s.system.gateway_pid||"—";
  $("kLast").textContent=s.system.last_activity||"—";
  $("kState").textContent=(s.system.gateway_state||"—").toUpperCase();

  $("dBot").textContent=s.discord.bot||"—";
  const ds=$("dState"),st=(s.discord.state||"offline");
  ds.textContent=st.toUpperCase(); ds.className="badge "+(st==="connected"?"ok":"bad");
  $("dMsgs").textContent=s.discord.msgs_today;
  $("dResp").textContent=s.discord.responses_today;
  $("dAvg").textContent=s.discord.avg_response!=null?s.discord.avg_response+"s":"—";
  const lr=s.discord.last_response;
  $("dLast").textContent=lr?(lr.chars+" chars · "+lr.time+"s"):"—";

  updateHardware(s);

  $("aModel").textContent=s.agent.model||"idle";
  $("aProv").textContent=s.agent.provider||"—";
  $("aCalls").textContent=s.agent.api_today;
  $("aLat").textContent=s.agent.avg_latency!=null?s.agent.avg_latency+"s":"—";
  $("aTokens").textContent=fmt(s.agent.tokens_today);
  $("aTools").textContent=(s.agent.recent_tools||[]).length;

  const tk=s.watchdog.task||{};
  const wt=$("wTask");
  wt.textContent=tk.present?(tk.status||"ACTIVE").toUpperCase():"MISSING";
  wt.className="badge "+(tk.present?"ok":"bad");
  $("wNext").textContent=tk.next_run||"—";
  $("wCount").textContent=s.watchdog.restarts;
  $("wLast").textContent=s.watchdog.last_restart||"none";

  $("eCount").textContent=s.errors.count_today+" today";
  const el=$("errList");
  el.innerHTML=s.errors.recent.length? s.errors.recent.slice().reverse().map(e=>
    `<div class="err ${e.level}"><span class="lv">${e.level}</span> ${esc(e.logger)}<span class="mg">${esc(e.text)}</span></div>`).join("")
    : '<div class="muted">no issues</div>';

  function renderMessages(){
    const board=$("msgBoard");
    const msgs = (s.unified_messages||[]).filter(m => selectedSource==='all' || m.source===selectedSource);
    if(!msgs.length){
      board.innerHTML='<div class="muted">no messages</div>';
      $("msgCount").textContent='0 messages';
      return;
    }
    $("msgCount").textContent=msgs.length+' messages';

    let html=`<div class="msg-header"><b>${esc(selectedSource==='all'?'All messages':selectedSource)}</b></div>`;

    let cur='';
    let rendered=0;
    msgs.forEach(m=>{
      const day=m.ts? m.ts.slice(0,10):'';
      if (day && day!==cur) {
        cur=day;
        if (day===s.server_date) {
          html+=`<div class="date-sep"><span>Today</span></div>`;
        } else if (day===new Date(Date.now()-86400000).toISOString().slice(0,10)) {
          html+=`<div class="date-sep"><span>Yesterday</span></div>`;
        } else {
          html+=`<div class="date-sep"><span>${esc(day)}</span></div>`;
        }
      }
      const name=m.user||(m.type==='out'?'nora':'?');
      const initials=name.slice(0,2).toUpperCase();
      const avatarUrl = (() => {
        const n = name.toLowerCase();
        if (n === 'nora' || n === 'hermes') return (s.avatars && s.avatars.nora) || '';
        if (n === 'murderszn') return (s.avatars && s.avatars.murderszn) || '';
        return '';
      })();
      const hue=(name.split('').reduce((a,b)=>a+b.charCodeAt(0),0)%360);
      const avatarBg=`hsl(${hue},55%,22%)`;
      const avatarColor=`hsl(${hue},75%,82%)`;
      const whoClass=m.type==='out'?'name-out':'name-in';
      const txt=esc(m.text || '');
      html+=`<div class="msg">
        <div class="avatar" style="${avatarUrl ? '' : `background:${avatarBg};color:${avatarColor}`}">${avatarUrl ? `<img src="${avatarUrl}" alt="${esc(name)}">` : initials}</div>
        <div style="flex:1;min-width:0">
          <div class="meta"><span class="name ${whoClass}">${esc(name)} </span><span style="color:var(--muted);margin-left:6px;font-size:.65rem">${esc(m.channel_name||m.source)}</span><span>${m.ts? m.ts.slice(11,16):''}</span></div>
          <div class="txt">${txt}</div>
        </div>
      </div>`;
      rendered++;
    });
    board.innerHTML=html;
  }

  function renderFah(){
    const wrap=$("fahWrap");
    const Units=(s.fah||[]);
    if(!Units.length){
      wrap.innerHTML='<div class="muted">no active units</div>';
      $("fahCount").textContent='';
      return;
    }
    $("fahCount").textContent=Units.length+' units';
    wrap.innerHTML = Units.map(u => {
      const pct = u.progress || '--';
      const barPct = (parseInt(pct) || 0);
      const status = u.status === 'interrupted' ? '⏸ INTERRUPTED' : '● running';
      const label = u.project ? `Project ${u.project}` : 'Unknown project';
      const detail = `Core ${u.core || '?'}` + (u.slot ? ` slot ${u.slot}` : '');
      const time = u.completed_steps ? `${u.completed_steps} / ${u.total_steps} steps` : '';
      return `<div class="fahrow">
        <div class="ico">${status}</div>
        <div class="lbl">${esc(label)}<br><span style="color:var(--muted);font-size:.62rem">${esc(detail)}</span></div>
        <div class="det">${esc(pct)}</div>
        <div class="bar"><span style="width:${barPct}%"></span></div>
        <div class="tm">${esc(time)}</div>
      </div>`;
    }).join('');
  }

  renderFah();
  renderMessages();

  const feed=$("feed"); feed.innerHTML=s.activity.length? s.activity.map(e=>{
    const who=e.type==="in"?`<span class="who">${esc(e.user||'user')}</span> `:`<span class="who">nora</span> `;
    return `<div class="ev ${e.type}"><span class="ico">${evIcon(e.type)}</span><div class="body">${who}<span class="msg">${esc(e.text)}</span></div><span class="tm">${hm(e.ts)}</span></div>`;
  }).join("") : '<div class="muted">no recent activity</div>';

}

refresh(); setInterval(refresh,5000);

document.querySelectorAll('#msgToggle button').forEach(btn=>{
  btn.onclick = () => {
    document.querySelectorAll('#msgToggle button').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    selectedSource = btn.getAttribute('data-src');
    renderMessages();
  };
});

/* ---- hardware sparklines ---- */
const HW = {cpu:[], gpu:[], ram:[], disk0:[], disk1:[], disk2:[]};
const MAX_PTS = 40;

function pushBuf(key, val){ HW[key].push(val); if(HW[key].length>MAX_PTS) HW[key].shift(); }

function drawSpark(canvasId, data, color){
  const c=$(canvasId); if(!c) return;
  const ctx=c.getContext('2d');
  const w=c.width, h=c.height;
  ctx.clearRect(0,0,w,h);
  if(!data||data.length<2) return;
  const max=Math.max(...data,1);
  const step=w/(MAX_PTS-1);
  ctx.beginPath();
  ctx.strokeStyle=color||'#fff';
  ctx.lineWidth=1.8;
  ctx.lineJoin='round';
  data.forEach((v,i)=>{
    const x=i*step;
    const y=h-(v/max)*(h-4)-2;
    if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.stroke();
  // glow fill
  ctx.lineTo((data.length-1)*step,h);
  ctx.lineTo(0,h);
  ctx.closePath();
  ctx.fillStyle='rgba(255,255,255,0.05)';
  ctx.fill();
}

function fmtDisk(pct){ return pct!=null? pct+'%':'--'; }
function fmtDiskSub(d){
  if(!d) return '';
  const gb = d.used_gb!=null && d.total_gb!=null ? `${d.used_gb}/${d.total_gb} GB` : '';
  return gb;
}
function fmtGpuSub(g){
  if(!g) return '';
  const mb = g.mem_used!=null && g.mem_total!=null ? `${g.mem_used}/${g.mem_total} MB` : '';
  const t = g.temp!=null ? `${g.temp}°C` : '';
  return [mb,t].filter(Boolean).join(' · ');
}
function fmtRamSub(r){
  if(!r) return '';
  return `${r.used_mb}/${r.total_mb} MB`;
}

function updateHardware(s){
  const hw=(s&&s.hardware)||{};
  const cpu=hw.cpu;
  const gpu=hw.gpu;
  const ram=hw.ram;
  const disks=hw.disks||[];

  if(cpu!=null){
    $('hCpu').textContent=cpu+'%'; pushBuf('cpu',cpu);
    $('hCpuSub').textContent='';
  } else { $('hCpu').textContent='--%'; $('hCpuSub').textContent='N/A'; }
  if(gpu!=null && typeof gpu==='object'){
    const u=gpu.usage;
    $('hGpu').textContent=(u!=null? u+'%':'--%'); pushBuf('gpu',u??0);
    $('hGpuSub').textContent=fmtGpuSub(gpu);
  } else { $('hGpu').textContent='--%'; $('hGpuSub').textContent='N/A'; }
  if(ram!=null && typeof ram==='object'){
    $('hRam').textContent=ram.pct+'%'; pushBuf('ram',ram.pct);
    $('hRamSub').textContent=fmtRamSub(ram);
  } else { $('hRam').textContent='--%'; $('hRamSub').textContent='N/A'; }

  for(let i=0;i<3;i++){
    const d=disks[i];
    const pct=d?d.pct:null;
    const used=d?d.pct||0:0;
    if(d!=null){
      $(`hDisk${i}`).textContent=fmtDisk(pct); pushBuf(`disk${i}`, used);
      $(`hDisk${i}Sub`).textContent=fmtDiskSub(d);
    } else {
      $(`hDisk${i}`).textContent='--%'; $(`hDisk${i}Sub`).textContent='N/A';
      pushBuf(`disk${i}`, 0);
    }
  }

  drawSpark('sparkCpu', HW.cpu, '#fff');
  drawSpark('sparkGpu', HW.gpu, '#fff');
  drawSpark('sparkRam', HW.ram, '#fff');
  drawSpark('sparkDisk0', HW.disk0, '#fff');
  drawSpark('sparkDisk1', HW.disk1, '#fff');
  drawSpark('sparkDisk2', HW.disk2, '#fff');
}

