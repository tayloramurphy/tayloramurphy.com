(() => {
  const canvas = document.getElementById("track");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  let tracks = [];
  let chosen = null;
  let fitted = [];
  let cum = [];
  let total = 0;
  let w = 0;
  let h = 0;
  let dpr = 1;
  let t = 0;
  let raf = 0;
  let last = 0;

  function pick(list) {
    return list[Math.floor(Math.random() * list.length)];
  }

  function fit(points) {
    const padX = w * 0.08;
    const padY = h * 0.10;
    const bw = Math.max(1, w - padX * 2);
    const bh = Math.max(1, h - padY * 2);
    // points already live in a padded unit square, aspect preserved
    let minX = 1, minY = 1, maxX = 0, maxY = 0;
    for (const [x, y] of points) {
      if (x < minX) minX = x;
      if (y < minY) minY = y;
      if (x > maxX) maxX = x;
      if (y > maxY) maxY = y;
    }
    const tw = Math.max(0.001, maxX - minX);
    const th = Math.max(0.001, maxY - minY);
    const scale = Math.min(bw / tw, bh / th);
    const ox = padX + (bw - tw * scale) / 2 - minX * scale;
    const oy = padY + (bh - th * scale) / 2 - minY * scale;
    return points.map(([x, y]) => [ox + x * scale, oy + y * scale]);
  }

  function distances(pts) {
    const out = [0];
    let acc = 0;
    for (let i = 1; i < pts.length; i++) {
      acc += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      out.push(acc);
    }
    return { cum: out, total: acc || 1 };
  }

  function along(progress) {
    const d = ((progress % 1) + 1) % 1 * total;
    let lo = 0;
    let hi = cum.length - 1;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (cum[mid] < d) lo = mid + 1;
      else hi = mid;
    }
    const i = Math.max(1, lo);
    const d0 = cum[i - 1];
    const d1 = cum[i];
    const u = d1 === d0 ? 0 : (d - d0) / (d1 - d0);
    const a = fitted[i - 1];
    const b = fitted[i];
    return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u];
  }

  function draw(progress) {
    ctx.clearRect(0, 0, w, h);
    if (!fitted.length) return;

    ctx.beginPath();
    ctx.moveTo(fitted[0][0], fitted[0][1]);
    for (let i = 1; i < fitted.length; i++) ctx.lineTo(fitted[i][0], fitted[i][1]);
    ctx.strokeStyle = "rgba(94, 177, 255, 0.26)";
    ctx.lineWidth = 1.35;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    ctx.stroke();

    if (reduce.matches) return;

    const [cx, cy] = along(progress);
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, 18);
    g.addColorStop(0, "rgba(255, 59, 48, 0.95)");
    g.addColorStop(1, "rgba(255, 59, 48, 0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(cx, cy, 18, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#FF3B30";
    ctx.beginPath();
    ctx.arc(cx, cy, 2.4, 0, Math.PI * 2);
    ctx.fill();

    const [tx, ty] = along(progress + 0.42);
    ctx.fillStyle = "rgba(94, 177, 255, 0.85)";
    ctx.beginPath();
    ctx.arc(tx, ty, 1.6, 0, Math.PI * 2);
    ctx.fill();
  }

  function layout() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = window.innerWidth;
    h = window.innerHeight;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (!chosen) return;
    fitted = fit(chosen.points);
    const d = distances(fitted);
    cum = d.cum;
    total = d.total;
  }

  function tick(now) {
    if (!last) last = now;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    t = (t + dt / 32) % 1;
    draw(t);
    raf = requestAnimationFrame(tick);
  }

  function start() {
    cancelAnimationFrame(raf);
    last = 0;
    layout();
    if (reduce.matches) {
      draw(0);
      return;
    }
    raf = requestAnimationFrame(tick);
  }

  function use(list) {
    tracks = list.filter((tr) => tr.points && tr.points.length >= 40);
    if (!tracks.length) return;
    chosen = pick(tracks);
    canvas.dataset.track = chosen.id;
    const label = document.getElementById("track-label");
    if (label) label.textContent = chosen.name;
    start();
  }

  window.addEventListener("resize", () => {
    if (!chosen) return;
    start();
  });
  reduce.addEventListener("change", start);

  fetch("/tracks.json")
    .then((r) => (r.ok ? r.json() : Promise.reject()))
    .then((data) => use(data.tracks || []))
    .catch(() => {});
})();
