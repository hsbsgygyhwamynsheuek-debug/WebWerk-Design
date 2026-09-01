/* Druckt die Anrufliste als Markdown - nach Ort sortiert.
   Aufruf: node scripts/anrufliste.js [Ort]
   Es werden nur Betriebe mit Status "offen" ausgegeben. */
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const W = path.join(__dirname, '..');
const L = JSON.parse(fs.readFileSync(path.join(W, 'daten', 'anrufliste.json'), 'utf8'));
const S = JSON.parse(fs.readFileSync(path.join(W, 'daten', 'sperrliste.json'), 'utf8'));

const pruef = nr => crypto.createHash('sha256')
  .update('webwerk-sperre:' + String(nr).replace(/\D/g, '')).digest('hex').slice(0, 16);
const gesperrt = new Set(S.gesperrt.map(e => e.pruefsumme));

const filter = (process.argv[2] || '').toLowerCase();
const zeilen = L
  .filter(b => b.status === 'offen')
  .filter(b => !gesperrt.has(pruef(b.tel)))
  .filter(b => !filter || b.ort.toLowerCase().includes(filter));

const heute = new Date().toLocaleDateString('de-DE');
let out = `# Anrufliste – Stand ${heute}\n\n`;
out += `${zeilen.length} Betriebe. Nur telefonisch – es werden keine E-Mails verschickt.\n\n`;
out += '| Betrieb | Ort | Telefon | Notiz |\n|---|---|---|---|\n';
for (const b of zeilen) {
  out += `| ${b.firma} | ${b.ort} | ${b.tel} | ${b.notiz || ''} |\n`;
}
out += `\n## Vor dem Anruf\n\n`;
out += `\`./scripts/pruefe-anruf.sh "<Nummer>"\` – meldet, ob die Nummer gesperrt ist.\n\n`;
out += `## Nach dem Anruf\n\n`;
out += `Sagt jemand Nein oder möchte nicht wieder angerufen werden:\n`;
out += `sofort in die Sperrliste, ohne Nachfrage.\n`;

const ziel = path.join(W, 'ANRUFLISTE.md');
fs.writeFileSync(ziel, out);
console.log(zeilen.length + ' Betriebe -> ANRUFLISTE.md');
