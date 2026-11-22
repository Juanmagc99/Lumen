param(
    [Parameter(Mandatory)]
    [ValidateSet('setup', 'dev-start', 'dev-stop', 'dev-restart', 'dev-status', 'dev-logs')]
    [string]$Command
)

# A 32-bit Make can launch 32-bit PowerShell, which cannot inspect 64-bit
# process paths. Re-run in the native host before checking process identity.
if ([Environment]::Is64BitOperatingSystem -and -not [Environment]::Is64BitProcess) {
    $nativePowerShell = Join-Path $env:WINDIR 'Sysnative\WindowsPowerShell\v1.0\powershell.exe'
    & $nativePowerShell -NoLogo -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath $Command
    exit $LASTEXITCODE
}

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
$runtime = Join-Path $root '.lumen-dev'
$decisionNames = @('LUMEN_DECISION_MODEL', 'LUMEN_DECISION_API_KEY', 'LUMEN_DECISION_TIMEOUT_SECONDS', 'LUMEN_RESPONSE_MODEL', 'LUMEN_RESPONSE_API_KEY', 'LUMEN_RESPONSE_TIMEOUT_SECONDS', 'LUMEN_EMBEDDING_API_KEY', 'LUMEN_EMBEDDING_TIMEOUT_SECONDS')
$decisionSettings = @{}
foreach ($name in $decisionNames) {
    $decisionSettings[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    [Environment]::SetEnvironmentVariable($name, $null, 'Process')
}

function Import-LocalConfig {
    $path = Join-Path $root '.env'
    if (-not (Test-Path -LiteralPath $path)) { return }
    $allowed = @('LUMEN_POSTGRES_USER', 'LUMEN_POSTGRES_DB', 'LUMEN_POSTGRES_PASSWORD', 'LUMEN_POSTGRES_PORT', 'LUMEN_ADMIN_USERNAME', 'LUMEN_ADMIN_PASSWORD', 'LUMEN_API_PORT', 'LUMEN_WEB_PORT', 'LUMEN_CLASSIFICATION_MAX_ATTEMPTS', 'LUMEN_CLASSIFICATION_RETRY_SECONDS', 'LUMEN_CLASSIFICATION_CLAIM_SECONDS', 'LUMEN_KNOWLEDGE_MAX_BYTES', 'LUMEN_RESPONSE_CONCURRENCY', 'LUMEN_RESPONSE_RATE_LIMIT', 'LUMEN_RESPONSE_RATE_WINDOW_SECONDS', 'LUMEN_RESPONSE_MAX_ATTEMPTS', 'LUMEN_RESPONSE_RETRY_SECONDS', 'LUMEN_RESPONSE_QUEUE_LIMIT', 'LUMEN_RESPONSE_INPUT_PRICE_PER_MILLION', 'LUMEN_RESPONSE_OUTPUT_PRICE_PER_MILLION', 'LUMEN_RESPONSE_CURRENCY', 'LUMEN_SIGNIN_FAILURE_LIMIT', 'LUMEN_EMBEDDING_MODEL', 'LUMEN_EMBEDDING_DIMENSIONS') + $decisionNames
    $lineNumber = 0
    foreach ($line in Get-Content -LiteralPath $path) {
        $lineNumber++
        $line = $line.Trim()
        if (-not $line -or $line.StartsWith('#')) { continue }
        if ($line -notmatch '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
            throw "Invalid .env entry on line $lineNumber. Use NAME=value."
        }
        $name = $Matches[1]
        $value = $Matches[2]
        if ($name -notin $allowed) { throw "Unsupported .env setting on line $lineNumber." }
        if ($value.StartsWith("'") -and $value.EndsWith("'") -and $value.Length -ge 2) {
            $value = $value.Substring(1, $value.Length - 2)
        } elseif ($value.Contains('"') -or $value.Contains("'") -or $value.Contains('#') -or $value.Contains('$')) {
            throw "Invalid .env value on line $lineNumber. Use a plain value or single quotes."
        }
        if ($name -in $decisionNames) {
            $decisionSettings[$name] = $value
        } else {
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
}

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. See README.md for prerequisites."
    }
}

function Invoke-Checked([string]$Name, [string[]]$Arguments) {
    & $Name @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE." }
}

function Initialize-Database {
    if (-not $env:LUMEN_POSTGRES_PASSWORD) {
        throw 'Set LUMEN_POSTGRES_PASSWORD in .env before starting. See README.md.'
    }
    Require-Command 'docker'
    Require-Command 'uv'
    if (-not $env:LUMEN_POSTGRES_USER -or -not $env:LUMEN_POSTGRES_DB) { throw 'Set LUMEN_POSTGRES_USER and LUMEN_POSTGRES_DB in .env before starting.' }
    if ($env:LUMEN_POSTGRES_PORT) {
        $databasePort = 0
        if (-not [int]::TryParse($env:LUMEN_POSTGRES_PORT, [ref]$databasePort) -or $databasePort -lt 1 -or $databasePort -gt 65535) {
            throw 'LUMEN_POSTGRES_PORT must be an integer between 1 and 65535.'
        }
    }
    # The API and migrations construct the same URL from the environment settings.
    Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
    Invoke-Checked 'docker' @('compose', '--project-name', 'lumen', 'up', '-d', '--wait', 'postgres')
    # Migration output can contain connection details; report a generic error instead.
    & uv run --project apps/api --locked alembic -c apps/api/alembic.ini upgrade head *> $null
    if ($LASTEXITCODE -ne 0) {
        throw 'Database migration failed. The database may still be running; inspect its status and credentials.'
    }
    try {
        & uv run --directory apps/api --locked python -m lumen.bootstrap.accounts bootstrap-env
        if ($LASTEXITCODE -ne 0) { throw 'Initial administrator setup failed. Check the local administrator settings.' }
    } finally {
        Remove-Item Env:LUMEN_ADMIN_PASSWORD -ErrorAction SilentlyContinue
        Remove-Item Env:LUMEN_ADMIN_USERNAME -ErrorAction SilentlyContinue
    }
}

function Get-ManagedProcess([string]$Name) {
    $path = Join-Path $runtime "$Name.json"
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    # Processes from a previous boot, including their children, cannot still exist.
    # Check this before looking up the PID, which Windows may already have reused.
    $startTicks = 0L
    if ([long]::TryParse([string]$record.startTicks, [ref]$startTicks) -and $startTicks -gt 0) {
        $bootTicks = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().Ticks
        if ($startTicks -lt $bootTicks) {
            Remove-Item -LiteralPath $path
            Write-Host "Removed obsolete $Name process record from before the last Windows boot."
            return $null
        }
    }
    $process = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
    if (-not $process) {
        throw "Recorded $Name process has exited; its child processes cannot be verified. Inspect and resolve $path before removing it."
    }
    if ($process.StartTime.ToUniversalTime().Ticks -ne [long]$record.startTicks -or $process.Path -ne $record.path) {
        throw "Cannot establish ownership of recorded $Name process. Inspect $path before removing it."
    }
    return $process
}

function Assert-PortAvailable([int]$Port) {
    if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
        throw "Port $Port is already in use. Stop the owner or select a different port."
    }
}

function Test-OwnedListener([int]$Port, [int]$RootId) {
    $listeners = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    if ($listeners.Count -eq 0) { return $false }
    foreach ($listener in $listeners) {
        $ownerId = [int]$listener.OwningProcess
        $seen = @{}
        while ($ownerId -and -not $seen.ContainsKey($ownerId)) {
            if ($ownerId -eq $RootId) { break }
            $seen[$ownerId] = $true
            $owner = Get-CimInstance Win32_Process -Filter "ProcessId = $ownerId" -ErrorAction SilentlyContinue
            if (-not $owner) { break }
            $ownerId = [int]$owner.ParentProcessId
        }
        if ($ownerId -ne $RootId) { throw "Port $Port is owned by an unrelated process; refusing to adopt it." }
    }
    return $true
}

function Start-Managed([string]$Name, [int]$Port, [string]$Program, [string[]]$Arguments) {
    $existing = Get-ManagedProcess $Name
    if ($existing) {
        $record = Get-Content -LiteralPath (Join-Path $runtime "$Name.json") -Raw | ConvertFrom-Json
        if ($record.port -ne $Port -or ($Port -gt 0 -and -not (Test-OwnedListener $Port $existing.Id))) {
            throw "$Name is running but does not own the configured port $Port. Stop it before changing ports."
        }
        Write-Host "$Name is already running."
        return
    }
    if ($Port -gt 0) { Assert-PortAvailable $Port }
    New-Item -ItemType Directory -Path $runtime -Force | Out-Null
    $process = Start-Process -FilePath $Program -ArgumentList $Arguments -WorkingDirectory $root -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $runtime "$Name.out.log") -RedirectStandardError (Join-Path $runtime "$Name.err.log")
    # Start-Process may not expose Path immediately; record the resolved executable.
    $record = @{ pid = $process.Id; startTicks = $process.StartTime.ToUniversalTime().Ticks; path = (Get-Item -LiteralPath $Program).FullName; port = $Port }
    $record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtime "$Name.json") -Encoding utf8
    $deadline = (Get-Date).AddSeconds(30)
    do {
        Start-Sleep -Milliseconds 300
        if (-not (Get-ManagedProcess $Name)) { throw "$Name exited during startup. See make dev-logs." }
        if ($Port -eq 0) { return }
        if (Test-OwnedListener $Port $process.Id) { return }
    } while ((Get-Date) -lt $deadline)
    throw "$Name did not start listening on port $Port. See make dev-logs and make dev-status."
}

function Stop-Managed([string]$Name) {
    $process = Get-ManagedProcess $Name
    if ($process) {
        & taskkill.exe /PID $process.Id /T /F | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Could not stop managed $Name process tree." }
    }
    $path = Join-Path $runtime "$Name.json"
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path }
    Write-Host "$Name stopped."
}

function Start-Environment {
    if (-not $env:LUMEN_POSTGRES_PASSWORD) { throw 'Set LUMEN_POSTGRES_PASSWORD in .env before starting. See README.md.' }
    Require-Command 'npm'
    # Check conflicts before changing the database or starting any processes.
    foreach ($service in @(@('api', $apiPort), @('web', $webPort))) {
        if (-not (Get-ManagedProcess $service[0])) { Assert-PortAvailable $service[1] }
    }
    Initialize-Database
    $env:LUMEN_API_TARGET = "http://127.0.0.1:$apiPort"
    $env:LUMEN_LOCAL_AUTH = 'true'
    $env:LUMEN_PUBLIC_ORIGIN = "http://127.0.0.1:$webPort"
    $uv = (Get-Command uv -CommandType Application | Select-Object -First 1).Source
    $node = (Get-Command node -CommandType Application | Select-Object -First 1).Source
    try {
        Start-Managed 'api' $apiPort $uv @('run', '--project', 'apps/api', '--locked', 'uvicorn', 'lumen.bootstrap.api:app', '--app-dir', 'apps/api', '--no-proxy-headers', '--host', '127.0.0.1', '--port', "$apiPort")
        try {
            foreach ($name in $decisionNames) {
                [Environment]::SetEnvironmentVariable($name, $decisionSettings[$name], 'Process')
            }
            Start-Managed 'worker' 0 $uv @('run', '--directory', 'apps/api', '--locked', 'python', '-m', 'lumen.bootstrap.worker')
        } finally {
            foreach ($name in $decisionNames) {
                [Environment]::SetEnvironmentVariable($name, $null, 'Process')
            }
        }
        $vite = Join-Path $root 'apps/web/node_modules/vite/bin/vite.js'
        if (-not (Test-Path -LiteralPath $vite)) { throw 'Vite is unavailable. Run make setup.' }
        Start-Managed 'web' $webPort $node @(('"' + $vite + '"'), 'apps/web', '--host', '127.0.0.1', '--port', "$webPort", '--strictPort', '--config', 'apps/web/vite.config.ts')
    } catch {
        Write-Host 'Startup was incomplete. Managed processes and PostgreSQL may still be running; inspect make dev-status and use make dev-stop when appropriate.'
        throw
    }
    Write-Host "API: http://127.0.0.1:$apiPort  Web: http://127.0.0.1:$webPort"
}

function Stop-Environment {
    Stop-Managed 'web'
    Stop-Managed 'worker'
    Stop-Managed 'api'
    Require-Command 'docker'
    # Compose interpolates the required password even for stop; this value is not used to alter the database.
    $savedPassword = $env:LUMEN_POSTGRES_PASSWORD
    try {
        if (-not $savedPassword) { $env:LUMEN_POSTGRES_PASSWORD = 'unused-for-stop' }
        Invoke-Checked 'docker' @('compose', '--project-name', 'lumen', 'stop', 'postgres')
    } finally { $env:LUMEN_POSTGRES_PASSWORD = $savedPassword }
}

try {
    Import-LocalConfig
    $apiPort = if ($env:LUMEN_API_PORT) { [int]$env:LUMEN_API_PORT } else { 8000 }
    $webPort = if ($env:LUMEN_WEB_PORT) { [int]$env:LUMEN_WEB_PORT } else { 5173 }
    switch ($Command) {
        'setup' {
            Require-Command 'uv'
            Require-Command 'npm'
            Invoke-Checked 'uv' @('sync', '--project', 'apps/api', '--locked', '--python', '3.13')
            Invoke-Checked 'npm' @('ci', '--prefix', 'apps/web')
        }
        'dev-start' {
            Start-Environment
        }
        'dev-stop' { Stop-Environment }
        'dev-restart' { Stop-Environment; Start-Environment }
        'dev-status' {
            foreach ($name in @('api', 'worker', 'web')) {
                $process = Get-ManagedProcess $name
                if ($process) { Write-Host "$name running (PID $($process.Id)); readiness is not verified." }
                else { Write-Host "$name stopped." }
            }
            if (-not $env:LUMEN_POSTGRES_PASSWORD) { $env:LUMEN_POSTGRES_PASSWORD = 'unused-for-status' }
            Require-Command 'docker'
            $containers = & docker compose --project-name lumen ps --all --quiet postgres
            if ($LASTEXITCODE -ne 0) { throw 'Could not retrieve PostgreSQL status from Docker Compose.' }
            if ($containers) { Invoke-Checked 'docker' @('compose', '--project-name', 'lumen', 'ps', '--all', 'postgres') }
            else { Write-Host 'postgres has not been created for the lumen Compose project.' }
        }
        'dev-logs' {
            foreach ($name in @('api', 'worker', 'web')) {
                foreach ($stream in @('out', 'err')) {
                    $log = Join-Path $runtime "$name.$stream.log"
                    Write-Host "--- $name $stream ---"
                    if (Test-Path -LiteralPath $log) { Get-Content -LiteralPath $log -Tail 100 } else { Write-Host 'No log available.' }
                }
            }
            if (-not $env:LUMEN_POSTGRES_PASSWORD) { $env:LUMEN_POSTGRES_PASSWORD = 'unused-for-logs' }
            Require-Command 'docker'
            $containers = & docker compose --project-name lumen ps --all --quiet postgres
            if ($LASTEXITCODE -ne 0) { throw 'Could not retrieve PostgreSQL status from Docker Compose.' }
            if ($containers) { Invoke-Checked 'docker' @('compose', '--project-name', 'lumen', 'logs', '--tail', '100', 'postgres') }
            else { Write-Host 'postgres: No log available.' }
        }
        default { throw "The $Command command is not implemented yet." }
    }
} catch {
    Write-Error $_
    exit 1
}
