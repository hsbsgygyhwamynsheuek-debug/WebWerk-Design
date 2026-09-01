/* Traegt ein, dass ein Betrieb am Telefon erlaubt hat, ihm eine Mail zu schicken.
   Aufruf: node scripts/erlaubnis.js "<Firma>" "<E-Mail>" [--seite-online]

   Nur wer hier eingetragen ist, darf eine Mail bekommen. Das ist der einzige
   Weg - es gibt keine Abkuerzung und keinen Schalter, der das ueberspringt. */
const fs = require('fs'), path = require('path');
const P = path.join(__dirname, '..', 'daten', 'anrufliste.json');

const [, , firmaArg, mailArg, ...rest] = process.argv;
if (!firmaArg || !mailArg) {
  console.error('Aufruf: node scripts/erlaubnis.js "<Firma>" "<E-Mail>" [--seite-online]');
  process.exit(2);
}
if (!/^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$/.test(mailArg)) {
  console.error('Das sieht nicht nach einer E-Mail-Adresse aus: ' + mailArg);
  process.exit(2);
}

const liste = JSON.parse(fs.readFileSync(P, 'utf8'));
const treffer = liste.filter(b => b.firma.toLowerCase().includes(firmaArg.toLowerCase()));

if (treffer.length === 0) { console.error('Betrieb nicht gefunden: ' + firmaArg); process.exit(1); }
if (treffer.length > 1) {
  console.error('Mehrere Treffer, bitte genauer angeben:');
  treffer.forEach(b => console.error('  - ' + b.firma));
  process.exit(2);
}

const b = treffer[0];
b.mail_erlaubt = true;
b.mail = mailArg;
b.erlaubt_am = new Date().toISOString().slice(0, 10);
b.status = 'angerufen';
if (rest.includes('--seite-online')) b.seite_online_erlaubt = true;

fs.writeFileSync(P, JSON.stringify(liste, null, 1));

console.log('Eingetragen:');
console.log('  Betrieb:  ' + b.firma + ' · ' + b.ort);
console.log('  E-Mail:   ' + b.mail);
console.log('  Erlaubt:  ' + b.erlaubt_am + ' (telefonisch)');
console.log('  Seite darf online: ' + (b.seite_online_erlaubt ? 'ja' : 'nein'));
console.log();
console.log('Jetzt darf eine Mail geschrieben werden.');
