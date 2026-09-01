/* Die einzige erlaubte Verkaufsmail: an einen Betrieb, der am Telefon
   ausdruecklich gesagt hat, dass er sie bekommen moechte.

   Aufruf: node scripts/mail-nach-anruf.js "<Firma>"

   Das Skript weigert sich, wenn keine Erlaubnis eingetragen ist. */
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const W = path.join(__dirname, '..');
const liste = JSON.parse(fs.readFileSync(path.join(W, 'daten', 'anrufliste.json'), 'utf8'));
const sperre = JSON.parse(fs.readFileSync(path.join(W, 'daten', 'sperrliste.json'), 'utf8'));

const hash = nr => crypto.createHash('sha256')
  .update('webwerk-sperre:' + String(nr).replace(/\D/g, '')).digest('hex').slice(0, 16);
const gesperrt = new Set(sperre.gesperrt.map(e => e.pruefsumme));

const suche = (process.argv[2] || '').toLowerCase();
if (!suche) { console.error('Aufruf: node scripts/mail-nach-anruf.js "<Firma>"'); process.exit(2); }

const treffer = liste.filter(b => b.firma.toLowerCase().includes(suche));
if (treffer.length !== 1) {
  console.error(treffer.length === 0 ? 'Betrieb nicht gefunden.' : 'Mehrere Treffer.');
  treffer.forEach(b => console.error('  - ' + b.firma));
  process.exit(1);
}
const b = treffer[0];

if (gesperrt.has(hash(b.tel))) { console.error('GESPERRT. Keine Mail.'); process.exit(1); }
if (!b.mail_erlaubt || !b.mail) {
  console.error('KEINE ERLAUBNIS. Erst anrufen und fragen, dann');
  console.error('node scripts/erlaubnis.js "' + b.firma + '" "<E-Mail>"');
  process.exit(1);
}

const e = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const C = { papier: '#FAF9F6', tinte: '#1A1A1B', grau: '#5C5A57', linie: '#E2DFD9', akzent: '#C2410C' };
const li = t => `<tr><td style="padding:0 0 10px 0;vertical-align:top;width:22px;color:${C.akzent};font-weight:700;line-height:1.5">›</td>
  <td style="padding:0 0 10px 0;font-size:16px;line-height:1.55;color:${C.tinte}">${t}</td></tr>`;

const html = `<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#EFEDE8">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">Wie eben besprochen – Ihr Entwurf.</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EFEDE8;padding:24px 12px">
<tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
 style="max-width:600px;background:${C.papier};border:1px solid ${C.linie};border-radius:14px;overflow:hidden;
        font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">

  <tr><td style="padding:30px 30px 6px 30px">
    <div style="font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:${C.akzent};font-weight:700">
      WebWerk Design · Jena</div>
    <h1 style="margin:14px 0 10px;font-size:29px;line-height:1.15;color:${C.tinte}">
      Wie eben besprochen.</h1>
    <p style="margin:0;font-size:17px;line-height:1.55;color:${C.tinte}">
      Guten Tag, hier wie am Telefon vereinbart die Unterlagen zu dem kostenlosen
      Website-Entwurf für <b>${e(b.firma)}</b>.</p>
  </td></tr>

  <tr><td style="padding:18px 30px 0">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:#EEF3EE;border-left:4px solid #2F6B3A;border-radius:0 8px 8px 0">
      <tr><td style="padding:16px 18px;font-size:16px;line-height:1.6;color:${C.tinte}">
        <b>Der Entwurf steht nicht im Internet.</b> Er liegt bei mir. Ihre Angaben
        habe ich nirgends veröffentlicht. Online geht die Seite erst, wenn Sie es
        ausdrücklich möchten – und dann stehe im Impressum ich als Verantwortlicher,
        nicht Sie.
      </td></tr></table>
  </td></tr>

  <tr><td style="padding:22px 30px 4px 30px">
    <h2 style="margin:0 0 14px;font-size:19px;color:${C.tinte}">Wie es weitergeht</h2>
    <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
      ${li('<b>Ich komme vorbei.</b> Ich zeige Ihnen die Seite auf dem Laptop. Dauert keine Viertelstunde.')}
      ${li('<b>Sie sagen, was anders soll.</b> Ich ändere es, so oft Sie möchten.')}
      ${li('<b>Erst wenn Sie zufrieden sind</b>, geht die Seite online – oder eben nicht.')}
    </table>
  </td></tr>

  <tr><td style="padding:8px 30px 0">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:#F3F1EC;border-left:4px solid ${C.akzent};border-radius:0 8px 8px 0">
      <tr><td style="padding:16px 18px;font-size:15px;line-height:1.6;color:${C.tinte}">
        <b>Kostenlos, und zwar wirklich.</b> Ich bin 14, gehe zur Schule und sammle
        Erfahrung. Sie zahlen nichts, Sie unterschreiben nichts, es kommt keine Rechnung.
      </td></tr></table>
  </td></tr>

  <tr><td style="padding:20px 30px 0">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:#F3F1EC;border-radius:8px">
      <tr><td style="padding:15px 18px;font-size:15px;line-height:1.6;color:${C.tinte}">
        <b>Wann Sie mich erreichen.</b> Bis 16 Uhr bin ich in der Schule, danach
        telefonisch unter <a href="tel:015144164431" style="color:${C.tinte}">0151 44164431</a>.
        Eine E-Mail können Sie mir jederzeit schreiben.
      </td></tr></table>
  </td></tr>

  <tr><td style="padding:22px 30px 30px">
    <p style="margin:0;font-size:15px;line-height:1.7;color:${C.tinte}">
      Freundliche Grüße<br>
      <b>Richard Baumgart</b><br>
      <span style="color:${C.grau}">WebWerk Design · Jena</span><br>
      <a href="tel:015144164431" style="color:${C.tinte};text-decoration:none">0151 44164431</a> ·
      <a href="mailto:richardbaumgart65@gmail.com" style="color:${C.akzent}">richardbaumgart65@gmail.com</a>
    </p>
    <p style="margin:18px 0 0;font-size:12px;line-height:1.55;color:${C.grau}">
      Sie erhalten diese E-Mail, weil Sie mir das am ${e(b.erlaubt_am)} am Telefon
      erlaubt haben. Möchten Sie keine weitere Nachricht, genügt ein kurzes „Nein" –
      dann lösche ich Ihre Daten sofort und vollständig (Art. 21 Abs. 2 DSGVO).<br>
      Diese E-Mail und der Entwurf wurden mit Unterstützung künstlicher Intelligenz
      erstellt – Artikel 50 der Verordnung (EU) 2024/1689.</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>`;

const ziel = path.join(W, 'entwuerfe', 'mails');
fs.mkdirSync(ziel, { recursive: true });
const key = b.firma.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
fs.writeFileSync(path.join(ziel, key + '.html'), html);

console.log('Erlaubnis vom ' + b.erlaubt_am + ' liegt vor.');
console.log('An:      ' + b.mail);
console.log('Betreff: Wie besprochen – Ihr Website-Entwurf');
console.log('Datei:   entwuerfe/mails/' + key + '.html');
