$ErrorActionPreference = 'Stop'
$root = Join-Path $env:LOCALAPPDATA 'NetPilot'
$bin = Join-Path $env:USERPROFILE 'bin'
$legacy = Join-Path $env:WINDIR 't.bat'
$backupDir = Join-Path $root 'backups'
Write-Host 'NetPilot installer: command t' -ForegroundColor Cyan

# Find a working Python; on a clean Windows PC download the official installer.
$python = $null
$candidates = @(
  (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'),
  (Join-Path $env:LOCALAPPDATA 'NetPilot\Python313\python.exe')
)
foreach ($candidate in $candidates) {
  if (Test-Path $candidate) {
    & $candidate -c 'import sys; assert sys.version_info >= (3, 10)' 2>$null
    if ($LASTEXITCODE -eq 0) { $python = $candidate; break }
  }
}
if (-not $python) {
  foreach ($command in @('py', 'python')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { continue }
    try {
      if ($command -eq 'py') {
        & py -3.13 -c 'import sys; assert sys.version_info >= (3, 10)' 2>$null | Out-Null
      } else {
        & python -c 'import sys; assert sys.version_info >= (3, 10)' 2>$null | Out-Null
      }
      if ($LASTEXITCODE -eq 0) { $python = $command; break }
    } catch {}
  }
}
if (-not $python) {
  $pythonVersion = '3.13.7'
  $architecture = if ([Environment]::Is64BitOperatingSystem) { 'amd64' } else { 'win32' }
  if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64' -or $env:PROCESSOR_ARCHITEW6432 -eq 'ARM64') {
    $architecture = 'arm64'
  }
  $installerName = "python-$pythonVersion-$architecture.exe"
  $downloadUrl = "https://www.python.org/ftp/python/$pythonVersion/$installerName"
  $downloadDir = Join-Path $env:TEMP 'NetPilot-Setup'
  New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null
  $installerPath = Join-Path $downloadDir $installerName
  Write-Host "Python not found. Downloading Python $pythonVersion from python.org..." -ForegroundColor Cyan
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
  $signature = Get-AuthenticodeSignature -FilePath $installerPath
  if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation') {
    throw 'Downloaded Python installer failed signature verification. Installation cancelled.'
  }
  $targetPython = Join-Path $env:LOCALAPPDATA 'NetPilot\Python313'
  Write-Host 'Installing Python for current user (no administrator required)...' -ForegroundColor Cyan
  $arguments = @('/quiet', 'InstallAllUsers=0', "TargetDir=$targetPython", 'Include_pip=1',
                 'Include_launcher=0', 'PrependPath=0', 'Include_test=0')
  $process = Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -PassThru
  if ($process.ExitCode -ne 0 -and $process.ExitCode -ne 3010) {
    throw "Python installation failed with exit code $($process.ExitCode)."
  }
  $python = Join-Path $targetPython 'python.exe'
  if (-not (Test-Path $python)) {
    throw "Python installer finished, but python.exe was not found at $python."
  }
  Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
  Write-Host 'Python installed successfully.' -ForegroundColor Green
}

New-Item -ItemType Directory -Force -Path $root, $bin, $backupDir | Out-Null
$venv = Join-Path $root '.venv'
if ($python -eq 'py') { & py -3.13 -m venv $venv }
else { & $python -m venv $venv }
if ($LASTEXITCODE -ne 0) { throw 'Failed to create Python environment.' }
$venvPython = Join-Path $venv 'Scripts\python.exe'
& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $PSScriptRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed; existing installation was not switched.' }
& $venvPython -m py_compile (Join-Path $PSScriptRoot 'telnet_manager.py')
if ($LASTEXITCODE -ne 0) { throw 'Python syntax check failed; existing installation was not switched.' }

# Back up existing legacy script and current NetPilot script before replacing either.
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$current = Join-Path $root 'telnet_manager.py'
if (Test-Path $current) {
  Copy-Item $current (Join-Path $backupDir "telnet_manager-$stamp.py") -Force
}
if (Test-Path $legacy) {
  Copy-Item $legacy (Join-Path $backupDir "legacy-t-$stamp.bat") -Force
}
Copy-Item (Join-Path $PSScriptRoot 'telnet_manager.py') $current -Force
Copy-Item (Join-Path $PSScriptRoot 'version.json') (Join-Path $root 'version.json') -Force
Copy-Item (Join-Path $PSScriptRoot 'update.ps1') (Join-Path $root 'update.ps1') -Force

$cmd = '@echo off' + "`r`n" +
  'title Telnet %~1' + "`r`n" +
  '"%LOCALAPPDATA%\NetPilot\.venv\Scripts\python.exe" "%LOCALAPPDATA%\NetPilot\telnet_manager.py" %*' + "`r`n" +
  'if errorlevel 1 pause' + "`r`n"
Set-Content -Path (Join-Path $bin 't.cmd') -Value $cmd -Encoding ASCII
$sshCmd = '@echo off' + "`r`n" +
  'title SSH %~1' + "`r`n" +
  '"%LOCALAPPDATA%\NetPilot\.venv\Scripts\python.exe" "%LOCALAPPDATA%\NetPilot\telnet_manager.py" --ssh %*' + "`r`n" +
  'if errorlevel 1 pause' + "`r`n"
Set-Content -Path (Join-Path $bin 's.cmd') -Value $sshCmd -Encoding ASCII
& $venvPython $current --sync-launchers
if ($LASTEXITCODE -ne 0) { Write-Warning 'Some existing device launchers could not be synchronized.' }
$npCmd = '@echo off' + "`r`n" +
  'if /I "%~1"=="update" goto update' + "`r`n" +
  '"%LOCALAPPDATA%\NetPilot\.venv\Scripts\python.exe" "%LOCALAPPDATA%\NetPilot\telnet_manager.py" --np %*' + "`r`n" +
  'exit /b %errorlevel%' + "`r`n" +
  ':update' + "`r`n" +
  'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LOCALAPPDATA%\NetPilot\update.ps1"' + "`r`n"
Set-Content -Path (Join-Path $bin 'np.cmd') -Value $npCmd -Encoding ASCII

# A t.bat in the user profile takes precedence when CMD starts there.
# Preserve it, then forward it to the newly installed launcher.
$userLegacy = Join-Path $env:USERPROFILE 't.bat'
if (Test-Path $userLegacy) {
  $userLegacyText = Get-Content $userLegacy -Raw
  if ($userLegacyText -match 'TelnetManager[\\/]telnet_manager\.py') {
    Copy-Item $userLegacy (Join-Path $backupDir "user-t-$stamp.bat") -Force
    $forwardUser = '@echo off' + "`r`n" +
      'call "%USERPROFILE%\bin\t.cmd" %*' + "`r`n"
    Set-Content -Path $userLegacy -Value $forwardUser -Encoding ASCII
    Write-Host 'Migrated user-profile t.bat; backup saved.' -ForegroundColor Green
  } else {
    Write-Warning 'User-profile t.bat is unrecognized and was left unchanged.'
  }
}

# The legacy Windows folder is earlier on PATH. Repoint its existing t.bat only
# if it is our recognizable old launcher. Unknown launchers are not overwritten.
if (Test-Path $legacy) {
  $legacyText = Get-Content $legacy -Raw
  if ($legacyText -match 'TelnetManager[\\/]telnet_manager\.py|TelnetManager\\telnet_manager\.py') {
    try {
      $forward = '@echo off' + "`r`n" +
        'call "%USERPROFILE%\bin\t.cmd" %*' + "`r`n"
      Set-Content -Path $legacy -Value $forward -Encoding ASCII -ErrorAction Stop
      Write-Host 'Migrated existing C:\Windows\t.bat; backup saved.' -ForegroundColor Green
    } catch {
      Write-Warning 'Could not update C:\Windows\t.bat (administrator permission may be needed).'
      Write-Warning 'Old t command may still take priority. No legacy file was deleted.'
    }
  } else {
    Write-Warning 'Existing C:\Windows\t.bat is not recognized. Kept untouched.'
  }
}

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$parts = @($userPath -split ';' | Where-Object { $_ })
if ($parts -notcontains $bin) {
  [Environment]::SetEnvironmentVariable('Path', (($parts + $bin) -join ';'), 'User')
}
# Check the installed script and report actual resolution separately.
& $venvPython -m py_compile $current
if ($LASTEXITCODE -ne 0) { throw 'Installed script failed verification.' }
Write-Host 'NetPilot installed. Credentials remain in %USERPROFILE%\TelnetManager\credentials.json.' -ForegroundColor Green
Write-Host 'Open a NEW CMD and run: np help'
Write-Host 'Then connect using: t 10.137.1.19'
if (Test-Path $userLegacy) {
  $checkUser = Get-Content $userLegacy -Raw
  if ($checkUser -notmatch 'call\s+"%USERPROFILE%\\bin\\t\.cmd"') {
    Write-Warning 'User-profile t.bat may override NetPilot.'
  }
}
if (Test-Path $legacy) {
  $legacyText = Get-Content $legacy -Raw
  if ($legacyText -notmatch 'call\s+"%USERPROFILE%\\bin\\t\.cmd"') {
    Write-Warning 'Legacy t.bat may still be selected. Review where t before switching.'
  }
}
