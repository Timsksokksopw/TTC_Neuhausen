<?php
/*
 * Anmeldung der Redaktion (/admin) mit Name und Passwort.
 *
 * Sveltia CMS öffnet diese Seite in einem eigenen Fenster («Anmelden»). Wer
 * Name und Passwort richtig eingibt, bekommt den Zugangsschlüssel zu GitHub,
 * den der Server verwahrt – die Schreibenden brauchen kein eigenes Konto.
 * Weitergereicht wird er nur an ein Redaktionsfenster auf derselben Adresse,
 * im Ablauf wie bei Netlify und Decap CMS:
 *   Fenster → Redaktion  "authorizing:github"
 *   Redaktion → Fenster  dasselbe zurück
 *   Fenster → Redaktion  "authorization:github:success:{"token":"…","provider":"github"}"
 *
 * Schlüssel und Passwörter stehen in zugang.php daneben. Die Datei legt
 * veroeffentlichen.py beim Hochladen aus den GitHub-Secrets
 * REDAKTION_SCHLUESSEL und REDAKTION_PASSWOERTER an, die Passwörter nur als
 * Prüfsumme (PBKDF2-SHA256). Sie gehört nicht ins Repository, und die
 * .htaccess liefert sie nie aus.
 */

declare(strict_types=1);

ini_set('display_errors', '0');
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store');
header('Referrer-Policy: no-referrer');
header('X-Content-Type-Options: nosniff');
header("Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
    . "form-action 'self'; frame-ancestors 'none'; base-uri 'none'");

// Gegen Durchprobieren: nach so vielen Fehlversuchen von einer Adresse ist
// dort für den Rest der Sperrzeit Schluss.
const VERSUCHE = 5;
const SPERRZEIT = 900;
// Für unbekannte Namen wird gegen diese Prüfsumme gerechnet, damit die
// Antwort gleich lange dauert und nicht verrät, welche Namen es gibt.
const ATTRAPPE = 'pbkdf2-sha256$600000$AAAAAAAAAAAAAAAAAAAAAA==$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=';

function seite(string $inhalt, string $skript = ''): void
{
    echo <<<HTML
<!doctype html>
<html lang="de-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Anmelden – Redaktion TTC Neuhausen</title>
<style>
  body { max-width: 24rem; margin: 10vh auto; padding: 0 1.5rem; background: #F3F0E8; color: #14161B;
         font: 17px/1.5 system-ui, sans-serif; }
  h1 { margin: 0 0 1.2rem; font-size: 1.5rem; line-height: 1.2; }
  label { display: block; margin: 0 0 1rem; font-weight: 600; }
  input { display: block; box-sizing: border-box; width: 100%; margin-top: .3rem; padding: .6rem .7rem;
          border: 1px solid #5F636B; border-radius: 4px; background: #FFFFFF; font: inherit; }
  input:focus { outline: 3px solid #FF8A3D; outline-offset: 1px; }
  button { margin-top: .4rem; padding: .7rem 1.4rem; border: 0; border-radius: 4px; background: #204E94;
           color: #FFFFFF; font: inherit; font-weight: 700; cursor: pointer; }
  .meldung { padding: .6rem .8rem; border-left: 4px solid #FF8A3D; background: #FFFFFF; }
  .klein { margin-top: 1.6rem; font-size: 15px; color: #3E434C; }
</style>
</head>
<body>
{$inhalt}
{$skript}
</body>
</html>
HTML;
    exit;
}

/** Schickt das Ergebnis an das Redaktionsfenster und zeigt dazu einen Satz. */
function ende(string $status, array $inhalt, string $satz): void
{
    $nachricht = 'authorization:github:' . $status . ':'
        . json_encode($inhalt + ['provider' => 'github'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    $js = json_encode($nachricht, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_UNESCAPED_SLASHES);
    seite('<p>' . htmlspecialchars($satz, ENT_QUOTES, 'UTF-8') . '</p>', <<<HTML
<script>
(function () {
  var nachricht = {$js};
  if (!window.opener) return;
  function weiter(e) {
    if (e.source !== window.opener || e.origin !== window.location.origin || e.data !== "authorizing:github") return;
    window.removeEventListener("message", weiter);
    window.opener.postMessage(nachricht, window.location.origin);
  }
  window.addEventListener("message", weiter);
  window.opener.postMessage("authorizing:github", window.location.origin);
})();
</script>
HTML);
}

function fehler(string $text): void
{
    ende('error', ['error' => $text], $text . ' Dieses Fenster kann geschlossen werden.');
}

function formular(string $name, string $meldung): void
{
    $name = htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
    $meldung = $meldung === '' ? '' : '<p class="meldung" role="alert">' . htmlspecialchars($meldung, ENT_QUOTES, 'UTF-8') . '</p>';
    seite(<<<HTML
<h1>Redaktion TTC Neuhausen</h1>
{$meldung}
<form method="post">
  <label>Name <input name="name" value="{$name}" autocomplete="username" autocapitalize="none" required autofocus></label>
  <label>Passwort <input name="passwort" type="password" autocomplete="current-password" required></label>
  <button type="submit">Anmelden</button>
</form>
<p class="klein">Passwort vergessen? Unter <a href="passwort.html" target="_blank" rel="noopener">Passwort festlegen</a>
  ein neues wählen und die Prüfzeile an Tim schicken.</p>
HTML);
}

/** Wie _name() in veroeffentlichen.py: ohne Gross/klein und doppelte Leerzeichen. */
function vergleichbar(string $name): string
{
    $name = trim((string)preg_replace('/\s+/u', ' ', $name));
    return function_exists('mb_strtolower') ? mb_strtolower($name, 'UTF-8') : strtolower($name);
}

function passt(string $passwort, string $pruefsumme): bool
{
    $teile = explode('$', $pruefsumme);
    if (count($teile) !== 4 || $teile[0] !== 'pbkdf2-sha256') {
        return false;
    }
    $soll = (string)base64_decode($teile[3], true);
    $ist = hash_pbkdf2('sha256', $passwort, (string)base64_decode($teile[2], true), (int)$teile[1], 32, true);
    return $soll !== '' && hash_equals($soll, $ist);
}

/** Die Fehlversuche dieser Adresse in der Sperrzeit; die Adresse nur als Prüfsumme. */
function sperrdatei(): string
{
    return sys_get_temp_dir() . '/ttcn-anmeldung-' . hash('sha256', (string)($_SERVER['REMOTE_ADDR'] ?? '')) . '.json';
}

function fehlversuche(): array
{
    $text = @file_get_contents(sperrdatei());
    $liste = is_string($text) ? json_decode($text, true) : null;
    $grenze = time() - SPERRZEIT;
    return array_values(array_filter(is_array($liste) ? $liste : [], function ($zeit) use ($grenze) {
        return is_int($zeit) && $zeit > $grenze;
    }));
}

$datei = __DIR__ . '/zugang.php';
$zugang = is_file($datei) ? require $datei : null;
if (!is_array($zugang) || empty($zugang['schluessel']) || empty($zugang['personen'])) {
    fehler('Die Anmeldung ist auf dem Server noch nicht eingerichtet (zugang.php fehlt).');
}
if (($_GET['provider'] ?? 'github') !== 'github') {
    fehler('Unbekannter Anbieter.');
}

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
    formular('', '');
}

$name = substr((string)($_POST['name'] ?? ''), 0, 200);
$versuche = fehlversuche();
if (count($versuche) >= VERSUCHE) {
    formular($name, 'Zu viele Fehlversuche. Bitte in einer Viertelstunde noch einmal versuchen.');
}
$pruefsumme = $zugang['personen'][vergleichbar($name)] ?? null;
$richtig = passt(trim(substr((string)($_POST['passwort'] ?? ''), 0, 400)),
    is_string($pruefsumme) ? $pruefsumme : ATTRAPPE);
if ($richtig && is_string($pruefsumme)) {
    @unlink(sperrdatei());
    ende('success', ['token' => (string)$zugang['schluessel']], 'Angemeldet. Dieses Fenster schliesst sich gleich.');
}
$versuche[] = time();
@file_put_contents(sperrdatei(), json_encode($versuche), LOCK_EX);
sleep(1);
formular($name, 'Name oder Passwort stimmt nicht.');
