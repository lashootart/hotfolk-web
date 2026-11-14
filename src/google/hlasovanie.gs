/**
 * HOTFOLK® – Fotka mesiaca – hlasovanie (Google Apps Script)
 * Vlož do Google Tabuľky: Rozšírenia → Apps Script, ulož a nasaď ako webovú aplikáciu
 * (Spustiť ako: Ja, Prístup: Ktokoľvek). URL nasadenia vlož do content.py → VOTE_API.
 */
const SHEET = 'Hlasy';

function sheet_(name, header) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(header); sh.setFrozenRows(1); }
  return sh;
}

function out_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function counts_(round) {
  const sh = sheet_(SHEET, ['Čas', 'Kolo', 'Fotka', 'Meno', 'E-mail', 'Jazyk', 'Súhlas']);
  const rows = sh.getDataRange().getValues().slice(1);
  const c = {};
  rows.forEach(function (r) { if (String(r[1]) === round) c[r[2]] = (c[r[2]] || 0) + 1; });
  return c;
}

// GET ?round=2026-11 → {"ok":true,"counts":{"1":12,"2":8,"3":5}}
function doGet(e) {
  const round = String((e.parameter && e.parameter.round) || '');
  return out_({ ok: true, round: round, counts: counts_(round) });
}

// POST (text/plain JSON) {round, model, name, email, lang, consent, website}
function doPost(e) {
  let d;
  try { d = JSON.parse(e.postData.contents); } catch (err) { return out_({ ok: false, error: 'bad_request' }); }
  if (d.website) return out_({ ok: true });                       // robot (honeypot)
  const round = String(d.round || '').slice(0, 20);
  const model = String(d.model || '').slice(0, 10);
  const name = String(d.name || '').trim().slice(0, 80);
  const email = String(d.email || '').trim().toLowerCase().slice(0, 120);
  if (!round || !model || !name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || d.consent !== true) {
    return out_({ ok: false, error: 'invalid' });
  }
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const sh = sheet_(SHEET, ['Čas', 'Kolo', 'Fotka', 'Meno', 'E-mail', 'Jazyk', 'Súhlas']);
    const rows = sh.getDataRange().getValues().slice(1);
    const dup = rows.some(function (r) { return String(r[1]) === round && String(r[4]).toLowerCase() === email; });
    if (dup) return out_({ ok: false, error: 'duplicate', counts: counts_(round) });
    sh.appendRow([new Date(), round, model, name, email, String(d.lang || '').slice(0, 2), 'áno']);
  } finally { lock.releaseLock(); }
  return out_({ ok: true, counts: counts_(round) });
}

// Žrebovanie: v editore Apps Script vyber funkciu vyzrebuj a klikni Spustiť.
// Výsledok nájdeš v Zobraziť → Záznamy (Logs). Kolo uprav podľa potreby.
function vyzrebuj() {
  const round = '2026-11';
  const rows = sheet_(SHEET, []).getDataRange().getValues().slice(1).filter(function (r) { return String(r[1]) === round; });
  if (!rows.length) { Logger.log('Žiadne hlasy v kole ' + round); return; }
  const w = rows[Math.floor(Math.random() * rows.length)];
  Logger.log('Výherca kola ' + round + ': ' + w[3] + ' <' + w[4] + '>  (z ' + rows.length + ' hlasov)');
}
