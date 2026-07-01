(function initShaderBanners() {
  const banners = document.querySelectorAll('.shader-banner');
  if (!banners.length) return;

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const VS = 'attribute vec2 a; void main(){ gl_Position = vec4(a, 0.0, 1.0); }';

  const FS = `
precision highp float;
uniform vec2 u_res;
uniform float u_time;
uniform float u_seed;
uniform float u_scale;
uniform float u_density;
uniform vec3 u_yellow;
uniform vec3 u_black;

float hash21(vec2 p){
  p = fract(p * vec2(234.34, 435.345));
  p += dot(p, p + 34.23);
  return fract(p.x * p.y);
}

float nearHead(float order, float head){
  return 1.0 - step(2.0, abs(order - head));
}

void main(){
  float mn = sqrt(u_res.x * u_res.y);
  vec2 p = (gl_FragCoord.xy - 0.5 * u_res) / mn;
  p *= mix(1.2, 2.6, u_scale) * 3.0;
  p += vec2(fract(u_seed * 0.193), fract(u_seed * 0.317)) * 2.0;

  float tick = floor(u_time * 1.6);
  float freq = 5.0 + u_density * 7.0;
  vec2 gv = p * freq;
  vec2 id = floor(gv);
  vec2 f = fract(gv);

  float gutter = 0.05;
  float inBox = step(gutter, f.x) * step(f.x, 1.0 - gutter)
              * step(gutter, f.y) * step(f.y, 1.0 - gutter);

  float chunkRoll = hash21(id);
  vec2 cluster2 = floor(id / 2.0);
  vec2 cluster3 = floor(id / 3.0);
  vec2 clusterCoord = mix(cluster2, cluster3, step(0.58, chunkRoll));

  float clusterOrder = hash21(clusterCoord * 1.91 + vec2(u_seed * 0.13)) * 88.0;
  float progress = tick * 1.35;
  float addressed = step(clusterOrder, progress);

  float head0 = mod(tick * 1.9 + u_seed * 3.7, 88.0);
  float head1 = mod(tick * 2.7 + u_seed * 1.4, 88.0);
  float head2 = mod(tick * 1.3 + u_seed * 5.1, 88.0);
  float head3 = mod(tick * 3.1 + u_seed * 2.8, 88.0);

  float clusterActive = 0.0;
  clusterActive = max(clusterActive, nearHead(clusterOrder, head0));
  clusterActive = max(clusterActive, nearHead(clusterOrder, head1));
  clusterActive = max(clusterActive, nearHead(clusterOrder, head2));
  clusterActive = max(clusterActive, nearHead(clusterOrder, head3));

  float pulse = 1.0 - step(0.5, mod(tick, 2.0));
  clusterActive *= pulse;

  float cellOrder = hash21(id + vec2(u_seed * 0.29)) * 160.0;
  float sparkHead = mod(tick * 4.3 + u_seed * 7.2, 160.0);
  float cellSpark = nearHead(cellOrder, sparkHead) * pulse;
  float cellDone = step(cellOrder, tick * 2.2);

  float highlighted = clamp(
    max(addressed, clusterActive * 0.95) + max(cellSpark, cellDone) * 0.85,
    0.0, 1.0
  );

  float fill = inBox * (1.0 - highlighted);
  vec3 col = mix(u_yellow, u_black, fill);
  gl_FragColor = vec4(col, 1.0);
}`;

  const PARAMS = {
    seed: 2251,
    yellow: '#f9ae2a',
    black: '#0a0908',
    scale: 0.5,
    density: 0.55,
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
      u_time: gl.getUniformLocation(prog, 'u_time'),
      u_seed: gl.getUniformLocation(prog, 'u_seed'),
      u_scale: gl.getUniformLocation(prog, 'u_scale'),
      u_density: gl.getUniformLocation(prog, 'u_density'),
      u_yellow: gl.getUniformLocation(prog, 'u_yellow'),
      u_black: gl.getUniformLocation(prog, 'u_black'),
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

      const elapsed = prefersReducedMotion ? 0.0 : (now - t0) / 1000;

      gl.uniform2f(U.u_res, width, height);
      gl.uniform1f(U.u_time, elapsed);
      gl.uniform1f(U.u_seed, (PARAMS.seed % 10000) * 0.6180339887 % 12.566);
      gl.uniform1f(U.u_scale, PARAMS.scale);
      gl.uniform1f(U.u_density, PARAMS.density);
      gl.uniform3fv(U.u_yellow, hex2rgb(PARAMS.yellow));
      gl.uniform3fv(U.u_black, hex2rgb(PARAMS.black));

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