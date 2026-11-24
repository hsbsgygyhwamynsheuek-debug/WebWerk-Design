const VS = `
attribute vec2 a; varying vec2 vUv;
void main(){ vUv = a; gl_Position = vec4(a*2.0-1.0, 0.0, 1.0); }`;

const FS = `
precision highp float;
uniform sampler2D tex;
uniform vec2  texSize;
uniform vec3  kopfC[3];   // x, y, Radius
uniform vec4  kopfM[3];   // dx, dy, Drehung, Groessenaenderung
uniform vec3  mundC[3];   // x, y, Radius
uniform float mundA[3];   // 0 = zu, 1 = weit auf
uniform vec4  augeC[3];   // x, y, rx, ry
uniform float blinzel[3];
varying vec2 vUv;

void main(){
  vec2 p = vec2(vUv.x, 1.0-vUv.y) * texSize;
  vec2 off = vec2(0.0);
  for(int i=0;i<3;i++){
    /* Kopf: Drehung, Verschiebung und Atmen, weich auslaufend */
    vec2 d = p - kopfC[i].xy;
    float r = kopfC[i].z;
    float w = exp(-dot(d,d)/(r*r));
    float c = cos(kopfM[i].z), s = sin(kopfM[i].z);
    vec2 gedreht = vec2(c*d.x - s*d.y, s*d.x + c*d.y) * (1.0 + kopfM[i].w);
    off += w * ((gedreht - d) + kopfM[i].xy);
    /* Mund: oertliche Dehnung nach oben und unten */
    vec2 dm = p - mundC[i].xy;
    float rm = mundC[i].z;
    float wm = exp(-dot(dm,dm)/(rm*rm));
    /* Der Kiefer faellt staerker nach unten als die Oberlippe nach oben geht */
    float v = clamp(dm.y/rm, -1.0, 1.0);
    off.y += mundA[i] * 34.0 * wm * v * (v > 0.0 ? 1.0 : 0.34);
    /* Blinzeln: oertliche Stauchung auf Augenhoehe */
    vec2 de = (p - augeC[i].xy) / vec2(augeC[i].z, augeC[i].w);
    float we = exp(-dot(de,de)*1.4);
    off.y -= blinzel[i] * 30.0 * we * clamp(de.y, -1.0, 1.0);
  }
  /* p liegt in Bildkoordinaten mit y nach unten; die Textur ist genauso
     abgelegt, deshalb hier KEINE weitere Spiegelung. */
  vec2 uv = (p - off) / texSize;
  gl_FragColor = texture2D(tex, clamp(uv, 0.0005, 0.9995));
}`;

function baueWarp2(canvas, bild, FIGUR){
  const ORDNUNG=['K','P','A'];
  const gl = canvas.getContext('webgl', {antialias:false, preserveDrawingBuffer:true});
  const sh = (t,s)=>{ const o=gl.createShader(t); gl.shaderSource(o,s); gl.compileShader(o);
    if(!gl.getShaderParameter(o,gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
  const pr = gl.createProgram();
  gl.attachShader(pr, sh(gl.VERTEX_SHADER,VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER,FS));
  gl.linkProgram(pr); gl.useProgram(pr);
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([0,0,1,0,0,1,0,1,1,0,1,1]), gl.STATIC_DRAW);
  const la = gl.getAttribLocation(pr,'a'); gl.enableVertexAttribArray(la);
  gl.vertexAttribPointer(la,2,gl.FLOAT,false,0,0);
  const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D,t);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,bild);
  const u = n => gl.getUniformLocation(pr,n);
  gl.uniform2f(u('texSize'), bild.naturalWidth, bild.naturalHeight);
  const L = {kopfC:u('kopfC[0]'),kopfM:u('kopfM[0]'),mundC:u('mundC[0]'),
             mundA:u('mundA[0]'),augeC:u('augeC[0]'),blinzel:u('blinzel[0]')};
  const kopfC=[], mundC=[], augeC=[];
  ORDNUNG.forEach(k=>{ kopfC.push(...FIGUR[k].kopf); mundC.push(...FIGUR[k].mund); augeC.push(...FIGUR[k].auge); });
  gl.uniform3fv(L.kopfC,new Float32Array(kopfC));
  gl.uniform3fv(L.mundC,new Float32Array(mundC));
  gl.uniform4fv(L.augeC,new Float32Array(augeC));
  gl.viewport(0,0,canvas.width,canvas.height);

  return function zeichne(z){   /* z = {K:{dx,dy,rot,sc,mund,blinzel}, P:…, A:…} */
    const m=[], a=[], b=[];
    ORDNUNG.forEach(k=>{ const s=z[k]||{};
      m.push(s.dx||0, s.dy||0, s.rot||0, s.sc||0);
      a.push(s.mund||0); b.push(s.blinzel||0); });
    gl.uniform4fv(L.kopfM,new Float32Array(m));
    gl.uniform1fv(L.mundA,new Float32Array(a));
    gl.uniform1fv(L.blinzel,new Float32Array(b));
    gl.drawArrays(gl.TRIANGLES,0,6);
  };
}
/* Verschiebung eines Punktes – damit die leuchtenden Zahlen mitwippen */
function versatz2(px, py, z, FIGUR){
  const ORDNUNG=['K','P','A'];
  let ox=0, oy=0;
  ORDNUNG.forEach(k=>{
    const s=z[k]||{}, [cx,cy,r]=FIGUR[k].kopf;
    const dx=px-cx, dy=py-cy, w=Math.exp(-(dx*dx+dy*dy)/(r*r));
    const c=Math.cos(s.rot||0), si=Math.sin(s.rot||0), sc=1+(s.sc||0);
    ox += w*((c*dx - si*dy)*sc - dx + (s.dx||0));
    oy += w*((si*dx + c*dy)*sc - dy + (s.dy||0));
  });
  return [ox,oy];
}
