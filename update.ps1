$ErrorActionPreference = 'Stop'
$releaseRepo = 'karen101996/netpilot-releases'
$apiBase = "https://api.github.com/repos/$releaseRepo/contents"
$root = Join-Path $env:LOCALAPPDATA 'NetPilot'
$staging = Join-Path ([IO.Path]::GetTempPath()) ('netpilot-' + [guid]::NewGuid().ToString('N'))
function Download-ReleaseFile([string]$file, [string]$path) {
  $headers = @{ 'User-Agent' = 'NetPilot-Updater'; 'Accept' = 'application/vnd.github+json' }
  $response = Invoke-RestMethod -Uri "$apiBase/$file" -Headers $headers -TimeoutSec 30
  if (-not $response.content -or $response.encoding -ne 'base64') {
    throw "GitHub API did not return base64 content for $file"
  }
  $bytes = [Convert]::FromBase64String(($response.content -replace '\s', ''))
  [IO.File]::WriteAllBytes($path, $bytes)
  if ($response.sha -and (Git-Blob-Sha $path) -ne $response.sha) {
    throw "GitHub API SHA mismatch: $file"
  }
}
function Git-Blob-Sha([string]$path) {
  $bytes = [IO.File]::ReadAllBytes($path)
  $prefix = [Text.Encoding]::ASCII.GetBytes("blob $($bytes.Length)" + [char]0)
  $buffer = New-Object byte[] ($prefix.Length + $bytes.Length)
  [Array]::Copy($prefix, 0, $buffer, 0, $prefix.Length)
  [Array]::Copy($bytes, 0, $buffer, $prefix.Length, $bytes.Length)
  $sha = [Security.Cryptography.SHA1]::Create()
  try { return ([BitConverter]::ToString($sha.ComputeHash($buffer))).Replace('-', '').ToLowerInvariant() }
  finally { $sha.Dispose() }
}
New-Item -ItemType Directory -Path $staging -Force | Out-Null
try {
  Download-ReleaseFile "version.json" (Join-Path $staging 'version.json')
  $manifest = Get-Content (Join-Path $staging 'version.json') -Raw | ConvertFrom-Json
  if (-not $manifest.version -or -not $manifest.files) { throw 'Invalid release manifest.' }
  $installedVersion = '0.0.0'
  $localVersion = Join-Path $root 'version.json'
  if (Test-Path $localVersion) {
    $installedVersion = (Get-Content $localVersion -Raw | ConvertFrom-Json).version
  }
  Write-Host "NetPilot installed: $installedVersion | latest: $($manifest.version)"
  if ([version]$installedVersion -ge [version]$manifest.version) {
    Write-Host 'Already up to date.' -ForegroundColor Green
    exit 0
  }
  foreach ($file in @('install.ps1','telnet_manager.py','requirements.txt','update.ps1')) {
    $expected = [string]$manifest.files.$file
    if ($expected -notmatch '^[0-9a-f]{40}$') { throw "Invalid checksum for $file" }
    $target = Join-Path $staging $file
    Download-ReleaseFile $file $target
    if ((Git-Blob-Sha $target) -ne $expected) { throw "Checksum mismatch for $file. Try again later." }
  }
  Write-Host "Verified release $($manifest.version). Installing..." -ForegroundColor Cyan
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $staging 'install.ps1')
  if ($LASTEXITCODE -ne 0) { throw 'Installer failed; check output.' }
  Write-Host "NetPilot updated to $($manifest.version)." -ForegroundColor Green
} finally {
  Remove-Item $staging -Recurse -Force -ErrorAction SilentlyContinue
}
