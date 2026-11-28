/* 3D-Treppenrennen "MOTIVATION vs DISCIPLINE" mit Three.js.
   baueSzene(THREE, renderer, B, H, opt) liefert render(t): jeder Zeitpunkt wird vollstaendig aus t berechnet
   (deterministisch, daher Bild fuer Bild als Video renderbar). Derselbe Code laeuft im Three.js-Viewer-Connector. */
function baueSzene(THREE, renderer, B, H, opt) {
  opt = opt || {};
  const LINKS = opt.links || 'MOTIVATION', RECHTS = opt.rechts || 'DISCIPLINE', DAUER = opt.dauer || 18;
  const NS = 20, TIEFE = 0.55, HOEHE = 0.32, BREITE = 3.2;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputEncoding = THREE.sRGBEncoding; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.85;
  const szene = new THREE.Scene();
  szene.background = new THREE.Color(0x020203); szene.fog = new THREE.Fog(0x020203, 10, 24);
  const kamera = new THREE.PerspectiveCamera(38, B / H, 0.1, 100);

  /* Licht: schwaches Grundlicht, warmes Schluesellicht mit Schatten, Spot oben fuer das Ziel */
  szene.add(new THREE.HemisphereLight(0x8899aa, 0x050505, 0.12));
  const key = new THREE.DirectionalLight(0xffe7cc, 0.55); key.position.set(-4, 9, -6); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -8, right: 14, top: 10, bottom: -4, near: 1, far: 40 }); key.shadow.bias = -0.0004;
  szene.add(key); szene.add(key.target); key.target.position.set(5, 2, 0);
  const spot = new THREE.SpotLight(0xfff3d6, 0, 14, 0.38, 0.6, 1.2); spot.castShadow = true; spot.shadow.mapSize.set(1024, 1024);
  spot.position.set(NS * TIEFE, NS * HOEHE + 6, 0.55); szene.add(spot); spot.target.position.set(NS * TIEFE, NS * HOEHE, 0.55); szene.add(spot.target);

  /* Treppe aus Beton mit Lichtleisten und Stufennummern */
  const beton = new THREE.MeshStandardMaterial({ color: 0x34322f, roughness: 0.92, metalness: 0.0 });
  const beton2 = new THREE.MeshStandardMaterial({ color: 0x2e2c2a, roughness: 0.95 });
  const led = new THREE.MeshStandardMaterial({ color: 0xffe2b0, emissive: 0xffc878, emissiveIntensity: 2.2 });
  const zahlTex = k => { const c = document.createElement('canvas'); c.width = 128; c.height = 64; const g = c.getContext('2d');
    g.fillStyle = 'rgba(255,240,220,.85)'; g.font = 'bold 44px Inter, Arial'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(String(k), 64, 34);
    const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; return t; };
  const stufenMat = [];
  for (let k = 1; k <= NS; k++) {
    const h = k * HOEHE, m = new THREE.Mesh(new THREE.BoxGeometry(TIEFE, h, BREITE), k % 2 ? beton : beton2);
    m.position.set(k * TIEFE, h / 2, 0); m.castShadow = true; m.receiveShadow = true; szene.add(m);
    const l = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.045, BREITE - 0.1), led.clone()); l.position.set(k * TIEFE - TIEFE / 2 + 0.02, h - 0.03, 0); szene.add(l); stufenMat.push(l.material);
    const n = new THREE.Mesh(new THREE.PlaneGeometry(0.26, 0.13), new THREE.MeshBasicMaterial({ map: zahlTex(k), transparent: true, fog: true }));
    n.position.set(k * TIEFE - TIEFE / 2 - 0.002, h - 0.13, -1.05); n.rotation.y = -Math.PI / 2; szene.add(n);
  }
  for (let k = 2; k <= NS; k += 4) { const pl = new THREE.PointLight(0xffc878, 0.55, 3.2, 2); pl.position.set(k * TIEFE - 0.2, k * HOEHE + 0.25, 0); szene.add(pl); }
  const boden = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: 0x0c0c0c, roughness: 1 }));
  boden.rotation.x = -Math.PI / 2; boden.receiveShadow = true; szene.add(boden);
  const wand = new THREE.Mesh(new THREE.PlaneGeometry(60, 30), new THREE.MeshStandardMaterial({ color: 0x090909, roughness: 1 }));
  wand.position.set(8, 8, 2.4); wand.rotation.y = Math.PI; szene.add(wand);

  /* Lichtkegel am Ziel (sichtbarer Strahl) */
  const kegel = new THREE.Mesh(new THREE.ConeGeometry(1.25, 6, 40, 1, true), new THREE.MeshBasicMaterial({ color: 0xfff1d0, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending }));
  kegel.position.set(NS * TIEFE, NS * HOEHE + 3, 0.55); szene.add(kegel);

  /* Gelenkfigur: Huefte, Knie, Schultern, Ellbogen */
  const figur = (farbe) => {
    const mat = new THREE.MeshStandardMaterial({ color: farbe, roughness: 0.55, metalness: 0.0, emissive: 0x000000 });
    const teil = (r, l) => { const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, l, 6, 14), mat); m.castShadow = true; return m; };
    const wurzel = new THREE.Group(), koerper = new THREE.Group(); wurzel.add(koerper);
    const rumpf = teil(0.1, 0.3); rumpf.position.y = 0.74; koerper.add(rumpf);
    const kopf = new THREE.Mesh(new THREE.SphereGeometry(0.115, 24, 18), mat); kopf.position.y = 1.03; kopf.castShadow = true; koerper.add(kopf);
    const glied = (y, z, l1, l2, r) => { const a = new THREE.Group(); a.position.set(0, y, z); koerper.add(a);
      const o = teil(r, l1); o.position.y = -l1 / 2 - r * 0.5; a.add(o); const g = new THREE.Group(); g.position.y = -l1 - r; a.add(g);
      const u = teil(r * 0.92, l2); u.position.y = -l2 / 2 - r * 0.5; g.add(u); return [a, g]; };
    const beinL = glied(0.53, 0.075, 0.2, 0.2, 0.055), beinR = glied(0.53, -0.075, 0.2, 0.2, 0.055);
    const armL = glied(0.88, 0.14, 0.16, 0.15, 0.042), armR = glied(0.88, -0.14, 0.16, 0.15, 0.042);
    szene.add(wurzel);
    return { wurzel, koerper, mat, gehen(ph, stark = 1) {
      const s = Math.sin(ph), c = Math.sin(ph + Math.PI);
      beinL[0].rotation.z = 0.55 * s * stark; beinL[1].rotation.z = -Math.max(0, 0.9 * Math.sin(ph - 1.2)) * stark;
      beinR[0].rotation.z = 0.55 * c * stark; beinR[1].rotation.z = -Math.max(0, 0.9 * Math.sin(ph + Math.PI - 1.2)) * stark;
      armL[0].rotation.z = -0.5 * s * stark; armL[1].rotation.z = 0.5 * stark; armR[0].rotation.z = -0.5 * c * stark; armR[1].rotation.z = 0.5 * stark; } };
  };
  const rechts = figur(0xf2f2f2), links = figur(0xf2f2f2);

  /* Namensschilder als Sprites */
  const schild = (text, farbe) => { const c = document.createElement('canvas'); c.width = 512; c.height = 128; const g = c.getContext('2d');
    g.font = '800 64px Inter, Arial'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = farbe; g.shadowColor = farbe; g.shadowBlur = 18; g.fillText(text, 256, 64);
    const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true, depthTest: false }));
    s.scale.set(1.25, 0.31, 1); szene.add(s); return s; };
  const schildR = schild(RECHTS, '#ffffff'), schildL = schild(LINKS, '#ff5a5f');

  /* Zeitlogik */
  const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), pr = (t, a, b) => cl((t - a) / (b - a));
  const eIO = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2, eOut = x => 1 - Math.pow(1 - x, 3);
  const auf = (kk) => { const f = Math.floor(kk), r = kk - f, glatt = r * r * (3 - 2 * r); return [kk * TIEFE + 0.05, (f + glatt) * HOEHE + Math.sin(Math.PI * r) * 0.1]; };
  const ANK = 0.8;

  function render(t) {
    const u = cl(t / DAUER);
    /* rechts: Stufe fuer Stufe nach oben */
    const kr = NS * pr(u, 0.05, ANK) * 0.97 + (u >= ANK ? 0.6 : 0);
    const [xr, yr] = auf(Math.min(NS - 0.4, kr));
    rechts.wurzel.position.set(xr, yr, 0.55); rechts.gehen(kr * Math.PI, u < ANK ? 1 : 0.15);
    const oben = eOut(pr(u, ANK, ANK + 0.06));
    if (u >= ANK) { rechts.koerper.rotation.z = 0; }
    /* links: sprintet, bricht auf Stufe 12 zusammen, kriecht */
    let kl = 12 * eOut(pr(u, 0, 0.36)), lieg = eOut(pr(u, 0.36, 0.44));
    if (u > 0.44) kl = 12 + 1.2 * pr(u, 0.44, 1);
    const [xl, yl] = auf(kl);
    links.wurzel.position.set(xl, yl + 0.16 * lieg, -0.55);
    links.koerper.rotation.z = -1.25 * lieg; links.gehen(kl * Math.PI * 1.15 + (u > 0.44 ? t * 3 : 0), u < 0.36 ? 1.25 : 0.25);
    links.mat.color.setRGB(0.95, 0.95 - 0.55 * lieg, 0.95 - 0.55 * lieg);
    /* Licht oben an, Lichtleisten der erreichten Stufen heller */
    spot.intensity = 14 * oben; kegel.material.opacity = 0.16 * oben;
    stufenMat.forEach((m, k) => { m.emissiveIntensity = (k + 1 <= Math.floor(kr + 0.01) ? 2.6 : 0.9) + 1.5 * oben * (k === NS - 1 ? 1 : 0); });
    /* Schilder */
    schildR.position.set(xr, yr + 1.45, 0.55); schildL.position.set(xl + (lieg > 0.5 ? 0.25 : 0), yl + (lieg > 0.5 ? 0.75 : 1.45), -0.55);
    /* Kamera: folgt dem Rennen von schraeg vorne, faehrt zum Schluss zurueck */
    const fx = (xr + xl) / 2, fy = (yr + yl) / 2 + 0.7, abst = Math.abs(xr - xl);
    const weit = eIO(pr(u, 0.78, 0.95)), dreh = -1.02 + 0.32 * u;
    const ab = 6.4 + 0.9 * abst + 3.4 * weit;
    kamera.position.set(fx + Math.sin(dreh) * ab - 0.8, fy + 1.9 + 2.0 * weit, -Math.cos(dreh) * ab);
    kamera.lookAt(fx + 0.4 + 1.5 * weit, fy - 0.2 + 0.6 * weit, 0.45 * (1 - weit));
    renderer.render(szene, kamera);
  }
  return { render, szene, kamera };
}
if (typeof module !== 'undefined') module.exports = { baueSzene };
