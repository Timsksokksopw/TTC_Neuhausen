# hol-dokumente.ps1 — holt die Vereinsdokumente von der bisherigen
# Website nach site\assets\dokumente\.
#
# ERZEUGT VON build.py — nicht von Hand ändern. Die Liste steht in
# vorlage/dokumente.py; nach einer Änderung dort einmal build.py.
#
# Starten: hol-dokumente.bat doppelklicken. Oder in PowerShell:
#   powershell -ExecutionPolicy Bypass -File .\hol-dokumente.ps1

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'   # sonst ist es zehnmal langsamer

$ziel = Join-Path $PSScriptRoot 'site\assets\dokumente'
New-Item -ItemType Directory -Force -Path $ziel | Out-Null

$dateien = @(
  @{ name = 'statuten.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2026/01/Statuten_Ausgabe_2025_12.pdf' }
  @{ name = 'spesenreglement.pdf'; url = 'https://www.ttc-neuhausen.ch/_data/pdf/ttcn_spesenreglement_2022-12.pdf' }
  @{ name = 'spesenformular.xlsx'; url = 'https://www.ttc-neuhausen.ch/_data/pdf/ttcn_spesenformular.xlsx' }
  @{ name = 'hallentarife-ttz-ebnat.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2024/05/TTZ-Ebnat-_Hallentarife.pdf' }
  @{ name = 'hallenreglement.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2026/04/2603-TTCN-Hallenreglement.pdf' }
  @{ name = 'helfereinsatzreglement.docx'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/Helfereinsatz_Reglement_Okt25.docx' }
  @{ name = 'maturaarbeit-tischtennisschlag.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/03/MA2024_DiephysikalischeBeschreibungeinesTischtennisschlages_ElioZarotti.pdf' }
  @{ name = 'beitritt-aktivplus.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/Beitrittserklaerungen-AktivPlus.pdf' }
  @{ name = 'beitritt-aktivplus-nachwuchs.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/Beitrittserklaerungen-AktivPlus-Nachwuchs.pdf' }
  @{ name = 'beitritt-aktivplus-studenten.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/Beitrittserklaerungen-AktivPlus-Studenten-und-Lehrling.pdf' }
  @{ name = 'beitritt-aktivplus-senioren.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/Beitrittserklaerungen-AktivPlus-Senioren.pdf' }
  @{ name = 'beitritt-aktiv.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/Beitrittserklaerungen-Aktiv.pdf' }
  @{ name = 'beitritt-damenverein.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/Beitrittserklaerungen-Damenverein.pdf' }
  @{ name = 'beitritt-passive.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2025/10/Beitrittserklaerungen-Passive.pdf' }
  @{ name = 'hallensportzentrum-flyer.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2026/04/Flyer_Erweiterung_Hallensportzentrum-1.pdf' }
  @{ name = 'hallensportzentrum-medienmitteilung.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2026/04/MM-Ausbauprojekt-1.pdf' }
  @{ name = 'hallensportzentrum-baustein.pdf'; url = 'https://www.ttc-neuhausen.ch/wp-content/uploads/2026/04/Flyer-Baustein-2026_compressed.pdf' }
)

Write-Host "Vereinsdokumente nach site\assets\dokumente\"
Write-Host "$($dateien.Count) Dateien`n"

$gut = 0
foreach ($d in $dateien) {
  $pfad = Join-Path $ziel $d.name
  if (Test-Path $pfad) {
    Write-Host ('  schon da   ' + $d.name)
    $gut++
    continue
  }
  $temp = [System.IO.Path]::GetTempFileName()
  try {
    Invoke-WebRequest -Uri $d.url -OutFile $temp -UseBasicParsing -TimeoutSec 60
  } catch {
    Write-Host ('  FEHLER     ' + $d.name + ' - ' + $_.Exception.Message) -ForegroundColor Red
    Remove-Item $temp -ErrorAction SilentlyContinue
    continue
  }
  # Eine Fehlerseite ist auch eine Antwort. Wer eine 2-kB-
  # «Seite nicht gefunden» als Statuten ablegt, merkt es erst,
  # wenn jemand sie oeffnet.
  $bytes = [System.IO.File]::ReadAllBytes($temp)
  $kopf = if ($bytes.Length -ge 4) { [System.Text.Encoding]::ASCII.GetString($bytes[0..3]) } else { '' }
  if ($bytes.Length -lt 4096 -and $kopf -ne '%PDF' -and $kopf.Substring(0,[Math]::Min(2,$kopf.Length)) -ne 'PK') {
    Write-Host ('  VERDAECHTIG ' + $d.name + ' - nur ' + $bytes.Length + ' Bytes, sieht nicht nach einem Dokument aus. Nicht gespeichert.') -ForegroundColor Yellow
    Remove-Item $temp -ErrorAction SilentlyContinue
    continue
  }
  Move-Item $temp $pfad -Force
  Write-Host ('  geholt     ' + $d.name.PadRight(38) + ('{0,6:N1}' -f ($bytes.Length / 1024)) + ' kB')
  $gut++
}

Write-Host "`n$gut von $($dateien.Count) bereit."
if ($gut -lt $dateien.Count) {
  Write-Host 'Die fehlenden bitte von Hand holen - die Adressen stehen bei'
  Write-Host 'jedem Eintrag in vorlage/dokumente.py unter herkunft.'
}
Write-Host ''
Read-Host 'Mit Enter schliessen'
