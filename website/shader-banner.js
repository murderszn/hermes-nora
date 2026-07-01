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
uniform vec3 u_c0, u_c1, u_c2, u_c3;

vec3 grad4(float t){
  t = clamp(t, 0.0, 1.0);
  vec3 c = mix(u_c0, u_c1, smoothstep(0.00, 0.55, t));
  c = mix(c, u_c2, smoothstep(0.55, 0.82, t));
  c = mix(c, u_c3, smoothstep(0.82, 1.00, t));
  return c;
}

void main(){
  vec2 uv = gl_FragCoord.xy / u_res;
  uv.y = 1.0 - uv.y;
  float mn = sqrt(u_res.x * u_res.y);
  vec2 p = (gl_FragCoord.xy - 0.5 * u_res) / mn;
  p *= mix(1.0, 2.5, u_scale) * 3.0;
  p += vec2(fract(u_seed * 0.193), fract(u_seed * 0.317)) * 2.0;

  float freq = 3.5 + u_density * 8.0;
  float gx = sin(p.x * freq + u_phase);
  float gy = sin(p.y * freq - u_phase);
  float lines = max(gx, gy);
  float nodes = gx * gy;
  float f = 0.5 + 0.5 * mix(lines, nodes, 0.28);

  float edge = 0.10 + u_detail * 0.06;
  f = smoothstep(0.5 - edge, 0.5 + edge, f);
  f = mix(0.62, 1.0, f);

  vec3 col = grad4(f);
  gl_FragColor = vec4(col, 1.0);
}`;

  const PARAMS = {
    seed: 2251,
    loop: 48,
    colors: ['#e09520', '#f9ae2a', '#fcc22e', '#fcd956'],
    scale: 0.55,
    density: 0.45,
    detail: 0.25,
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
        ? 0.0
        : (elapsed / PARAMS.loop * Math.PI * 2) % (Math.PI * 2);

      gl.uniform2f(U.u_res, width, height);
      gl.uniform1f(U.u_phase, phase);
      gl.uniform1f(U.u_seed, (PARAMS.seed % 10000) * 0.6180339887 % 12.566);
      gl.uniform1f(U.u_scale, PARAMS.scale);
      gl.uniform1f(U.u_density, PARAMS.density);
      gl.uniform1f(U.u_detail, PARAMS.detail);
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