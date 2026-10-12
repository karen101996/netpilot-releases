$ErrorActionPreference = 'Stop'
$root = Join-Path $env:LOCALAPPDATA 'NetPilot'
$bin = Join-Path $env:USERPROFILE 'bin'
$legacy = Join-Path $env:WINDIR 't.bat'
$backupDir = Join-Path $root 'backups'
Write-Host 'NetPilot installer: command t' -ForegroundColor Cyan

# Use an existing supported Python or install 3.13 via winget.
$python = $null
try {
  & py -3.13 -c 'import sys; assert sys.version_info >= (3, 10)' 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { $python = 'py' }
} catch {}
if (-not $python) {
  try {
    & python -c 'import sys; assert sys.version_info >= (3, 10)' 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $python = 'python' }
  } catch {}
}
if (-not $python) {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw 'Python 3.13 required; winget not found. Install Python then rerun.'
  }
  & winget install --id Python.Python.3.13 --exact --source winget --accept-source-agreements --accept-package-agreements
  if ($LASTEXITCODE -ne 0) { throw 'Python installation failed.' }
  $pythonPath = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'
  if (-not (Test-Path $pythonPath)) { throw 'Python installed but not found. Open a new shell and rerun INSTALL.bat.' }
  $python = $pythonPath
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
$npCmd = '@echo off' + "`r`n" +
  'if /I "%~1"=="update" goto update' + "`r`n" +
  'echo NetPilot: use np update to update. Telnet: t IP' + "`r`n" +
  'exit /b 1' + "`r`n" +
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
Write-Host 'Open a NEW CMD and run: where t'
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
