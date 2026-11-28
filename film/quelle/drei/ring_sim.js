/* Physik fuer "Which color escapes first?": Baelle in einem rotierenden Ring mit Luecke.
   Deterministisch (eigener Zufallsgenerator mit Startwert), feste Schrittweite.
   Ergebnis: Positionen je Videobild (30 fps) und alle Stoesse mit Zeitpunkt (fuer die Toene). */
function simuliere(seed, opt) {
  opt = opt || {};
  const R = 4.0, r = 0.32, G = 6.2, LUECKE = opt.luecke || 0.42, OMEGA = opt.omega || 0.55, DT = 1 / 600, FPS = 30, MAX = opt.max || 45;
  let s = seed >>> 0; const zufall = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  const farben = ['red', 'blue', 'green', 'yellow'];
  const b = farben.map((f, i) => ({ f, x: -1.6 + i * 1.07 + (zufall() - .5) * .3, y: 0.8 + (zufall() - .5) * .6, vx: (zufall() - .5) * 6, vy: zufall() * 3, raus: false, tRaus: null }));
  const bilder = [], stoesse = []; let gewinner = null, tGewinn = null, letzterStoss = b.map(() => -1);
  const schritte = Math.round(MAX / DT), jeBild = Math.round(1 / FPS / DT);
  for (let n = 0; n <= schritte; n++) {
    const t = n * DT, winkel = OMEGA * t;
    if (n % jeBild === 0) bilder.push({ w: winkel, b: b.map(k => [+k.x.toFixed(4), +k.y.toFixed(4)]) });
    if (gewinner !== null && t > tGewinn + 4) break;
    for (const k of b) { k.vy -= G * DT; k.x += k.vx * DT; k.y += k.vy * DT; }
    /* Ring: Luecke dreht sich mit; ausserhalb der Luecke wird reflektiert */
    b.forEach((k, i) => {
      if (k.raus) return;
      const d = Math.hypot(k.x, k.y);
      if (d + r >= R) {
        let a = Math.atan2(k.y, k.x) - winkel; a = Math.atan2(Math.sin(a), Math.cos(a));
        const inLuecke = Math.abs(a - Math.PI / 2) < LUECKE / 2 - r / R * 0.6;
        if (inLuecke) { if (d > R + r * 1.5) { k.raus = true; k.tRaus = t; if (gewinner === null) { gewinner = i; tGewinn = t; stoesse.push({ t, art: 'sieg', ball: i }); } } return; }
        const nx = k.x / d, ny = k.y / d, vn = k.vx * nx + k.vy * ny;
        if (vn > 0) {
          k.vx -= 2 * vn * nx; k.vy -= 2 * vn * ny;
          /* kleiner Schwung, damit die Baelle lebendig bleiben, mit Obergrenze */
          const v = Math.hypot(k.vx, k.vy), ziel = Math.min(11, v * 1.015 + 0.04); k.vx *= ziel / v; k.vy *= ziel / v;
          if (t - letzterStoss[i] > 0.06) { stoesse.push({ t, art: 'ring', ball: i, staerke: Math.min(1, v / 10) }); letzterStoss[i] = t; }
        }
        const p = (R - r) / d; k.x *= p; k.y *= p;
      }
    });
    /* Baelle untereinander: elastischer Stoss */
    for (let i = 0; i < b.length; i++) for (let j = i + 1; j < b.length; j++) {
      const A = b[i], B = b[j]; if (A.raus || B.raus) continue;
      const dx = B.x - A.x, dy = B.y - A.y, d = Math.hypot(dx, dy);
      if (d < 2 * r && d > 1e-6) {
        const nx = dx / d, ny = dy / d, rel = (B.vx - A.vx) * nx + (B.vy - A.vy) * ny;
        if (rel < 0) { A.vx += rel * nx; A.vy += rel * ny; B.vx -= rel * nx; B.vy -= rel * ny; stoesse.push({ t, art: 'ball', ball: i }); }
        const ue = (2 * r - d) / 2; A.x -= nx * ue; A.y -= ny * ue; B.x += nx * ue; B.y += ny * ue;
      }
    }
  }
  return { R, r, LUECKE, FPS, farben, bilder, stoesse, gewinner, tGewinn, seed };
}
if (typeof module !== 'undefined') module.exports = { simuliere };
