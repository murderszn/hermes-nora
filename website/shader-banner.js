(function initShaderBanners() {
  const banners = document.querySelectorAll('.shader-banner');
  if (!banners.length) return;

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const VS = 'attribute vec2 a; void main(){ gl_Position = vec4(a, 0.0, 1.0); }';

  const FS = `
precision highp float;
uniform vec2 u_res;
uniform float u_phase;
uniform float u_seed;
uniform float u_scale;
uniform float u_density;
uniform float u_detail;
uniform float u_grain;
uniform vec3 u_c0, u_c1, u_c2, u_c3;

float hash21(vec2 p){
  p = fract(p * vec2(234.34, 435.345));
  p += dot(p, p + 34.23);
  return fract(p.x * p.y);
}

vec2 fade(vec2 t) { return t*t*t*(t*(t*6.0-15.0)+10.0); }

vec4 permute(vec4 x) { return mod(((x*34.0)+1.0)*x, 289.0); }

float cnoise(vec2 P) {
  vec4 Pi = floor(P.xyxy) + vec4(0.0, 0.0, 1.0, 1.0);
  vec4 Pf = fract(P.xyxy) - vec4(0.0, 0.0, 1.0, 1.0);
  Pi = mod(Pi, 289.0);
  vec4 ix = Pi.xzxz; vec4 iy = Pi.yyww;
  vec4 fx = Pf.xzxz; vec4 fy = Pf.yyww;
  vec4 i = permute(permute(ix) + iy);
  vec4 gx = fract(i * (1.0 / 41.0)) * 2.0 - 1.0;
  vec4 gy = abs(gx) - 0.5;
  vec4 tx = floor(gx + 0.5);
  gx = gx - tx;
  vec2 g00 = vec2(gx.x,gy.x);
  vec2 g10 = vec2(gx.y,gy.y);
  vec2 g01 = vec2(gx.z,gy.z);
  vec2 g11 = vec2(gx.w,gy.w);
  vec4 norm = 1.79284291400159 - 0.85373472095314 * vec4(dot(g00, g00), dot(g01, g01), dot(g10, g10), dot(g11, g11));
  g00 *= norm.x; g01 *= norm.y; g10 *= norm.z; g11 *= norm.w;
  float n00 = dot(g00, vec2(fx.x, fy.x));
  float n10 = dot(g10, vec2(fx.y, fy.y));
  float n01 = dot(g01, vec2(fx.z, fy.z));
  float n11 = dot(g11, vec2(fx.w, fy.w));
  vec2 fade_xy = fade(Pf.xy);
  vec2 n_x = mix(vec2(n00, n01), vec2(n10, n11), fade_xy.x);
  return 2.3 * mix(n_x.x, n_x.y, fade_xy.y);
}

vec2 loopOff(){
  return vec2(cos(u_phase), sin(u_phase)) * 0.10;
}

vec3 grad4(float t){
  t = clamp(t, 0.0, 1.0);
  vec3 c = mix(u_c0, u_c1, smoothstep(0.00, 0.35, t));
  c = mix(c, u_c2, smoothstep(0.35, 0.70, t));
  c = mix(c, u_c3, smoothstep(0.70, 1.00, t));
  return c;
}

void main(){
  vec2 uv = gl_FragCoord.xy / u_res;
  uv.y = 1.0 - uv.y;
  float ar = u_res.x / u_res.y;
  vec2 sOff = vec2(fract(u_seed * 0.193), fract(u_seed * 0.317)) * 47.0;

  vec2 p = (uv - 0.5) * vec2(ar, 1.0) * mix(2.0, 6.0, u_scale) + sOff;
  mat2 rot = mat2(0.8, 0.6, -0.6, 0.8);
  float v = 0.0;
  float a = 0.5;
  vec2 q2 = p + loopOff();
  for (int i = 0; i < 8; i++){
    float fi = float(i);
    if (fi >= mix(3.0, 8.0, u_density)) break;
    v += a * abs(cnoise(q2 + loopOff()));
    q2 = rot * q2 * 2.0 + vec2(100.0);
    a *= mix(0.35, 0.65, u_detail);
  }

  vec3 col = grad4(clamp(v, 0.0, 1.0));
  col += u_c3 * pow(clamp(v, 0.0, 1.0), 3.0) * 0.2;
  col += (hash21(gl_FragCoord.xy + loopOff() * 91.3) - 0.5) * u_grain * 0.22;

  vec2 vig = uv * 2.0 - 1.0;
  col *= 1.0 - dot(vig, vig) * 0.16;

  gl_FragColor = vec4(col, 1.0);
}`;

  const PARAMS = {
    seed: 2251,
    loop: 6,
    colors: ['#0a0908', '#f9ae2a', '#fcc22e', '#000000'],
    scale: 0.6908631857900177,
    density: 0.594701655989847,
    detail: 0.7742052745347444,
    grain: 0.35,
  };

  function hex2rgb(h) {
    return [
      parseInt(h.slice(1, 3), 16) / 255,
      parseInt(h.slice(3, 5), 16) / 255,
      parseInt(h.slice(5, 7), 16) / 255,
    ];
  }

  function compileShader(gl, type, src) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, src);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.error(gl.getShaderInfoLog(shader));
      gl.deleteShader(shader);
      return null;
    }
    return shader;
  }

  banners.forEach((banner) => {
    const canvas = banner.querySelector('.shader-banner-canvas');
    if (!canvas) return;

    const gl = canvas.getContext('webgl', { alpha: false, antialias: false });
    if (!gl) {
      banner.classList.add('shader-banner--fallback');
      return;
    }

    const vs = compileShader(gl, gl.VERTEX_SHADER, VS);
    const fs = compileShader(gl, gl.FRAGMENT_SHADER, FS);
    if (!vs || !fs) {
      banner.classList.add('shader-banner--fallback');
      return;
    }

    const prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
      console.error(gl.getProgramInfoLog(prog));
      banner.classList.add('shader-banner--fallback');
      return;
    }
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const aLoc = gl.getAttribLocation(prog, 'a');
    gl.enableVertexAttribArray(aLoc);
    gl.vertexAttribPointer(aLoc, 2, gl.FLOAT, false, 0, 0);

    const U = {
      u_res: gl.getUniformLocation(prog, 'u_res'),
      u_phase: gl.getUniformLocation(prog, 'u_phase'),
      u_seed: gl.getUniformLocation(prog, 'u_seed'),
      u_scale: gl.getUniformLocation(prog, 'u_scale'),
      u_density: gl.getUniformLocation(prog, 'u_density'),
      u_detail: gl.getUniformLocation(prog, 'u_detail'),
      u_grain: gl.getUniformLocation(prog, 'u_grain'),
      u_c0: gl.getUniformLocation(prog, 'u_c0'),
      u_c1: gl.getUniformLocation(prog, 'u_c1'),
      u_c2: gl.getUniformLocation(prog, 'u_c2'),
      u_c3: gl.getUniformLocation(prog, 'u_c3'),
    };

    let width = 0;
    let height = 0;
    let rafId = 0;
    let visible = false;
    const t0 = performance.now();

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = banner.getBoundingClientRect();
      const nextW = Math.max(1, Math.round(rect.width * dpr));
      const nextH = Math.max(1, Math.round(rect.height * dpr));
      if (nextW === width && nextH === height) return;
      width = nextW;
      height = nextH;
      canvas.width = width;
      canvas.height = height;
      gl.viewport(0, 0, width, height);
    }

    function draw(now) {
      rafId = 0;
      if (!visible) return;

      const elapsed = (now - t0) / 1000;
      const phase = prefersReducedMotion
        ? 1.2
        : (elapsed / PARAMS.loop * Math.PI * 2) % (Math.PI * 2);

      gl.uniform2f(U.u_res, width, height);
      gl.uniform1f(U.u_phase, phase);
      gl.uniform1f(U.u_seed, (PARAMS.seed % 10000) * 0.6180339887 % 12.566);
      gl.uniform1f(U.u_scale, PARAMS.scale);
      gl.uniform1f(U.u_density, PARAMS.density);
      gl.uniform1f(U.u_detail, PARAMS.detail);
      gl.uniform1f(U.u_grain, PARAMS.grain);
      gl.uniform3fv(U.u_c0, hex2rgb(PARAMS.colors[0]));
      gl.uniform3fv(U.u_c1, hex2rgb(PARAMS.colors[1]));
      gl.uniform3fv(U.u_c2, hex2rgb(PARAMS.colors[2]));
      gl.uniform3fv(U.u_c3, hex2rgb(PARAMS.colors[3]));

      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      rafId = requestAnimationFrame(draw);
    }

    function start() {
      if (rafId) return;
      rafId = requestAnimationFrame(draw);
    }

    function stop() {
      if (!rafId) return;
      cancelAnimationFrame(rafId);
      rafId = 0;
    }

    resize();

    if ('ResizeObserver' in window) {
      const ro = new ResizeObserver(resize);
      ro.observe(banner);
    } else {
      window.addEventListener('resize', resize);
    }

    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        visible = entries.some((entry) => entry.isIntersecting);
        if (visible) start();
        else stop();
      }, { threshold: 0.01 });
      io.observe(banner);
    } else {
      visible = true;
      start();
    }
  });
})();