param(
    [string]$ApiHost = '127.0.0.1',
    [int]$ApiPort = 8000,
    [int]$StreamlitPort = 8501,
    [int]$VitePort = 5173,
    [switch]$NoStreamlit,
    [switch]$NoReact,
    [switch]$RunDemo,
    [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'

# Resolve absolute paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir '..')
$PythonPath = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$AppDir = Join-Path $ProjectRoot 'insider-detect'
$StreamlitApp = Join-Path $AppDir 'dashboard\streamlit_app.py'
$WebDir = Join-Path $ProjectRoot 'web-dashboard'

function Write-Info($m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Ok($m) { Write-Host "[OK]  $m" -ForegroundColor Green }
function Write-Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err($m) { Write-Host "[ERR] $m" -ForegroundColor Red }

function Test-Http200($url, [int]$timeoutSec=30) {
    $deadline = (Get-Date).AddSeconds($timeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
            if ($resp.StatusCode -eq 200) { return $true }
        } catch { Start-Sleep -Milliseconds 500 }
    }
    return $false
}

Write-Info "Stopping any previous node/npm/python (dev servers)"
Get-Process | Where-Object { $_.ProcessName -in @('node','npm','python') } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Info "Using Python at: $PythonPath"
if (-not (Test-Path $PythonPath)) { Write-Err "Python not found at $PythonPath"; exit 1 }

Write-Info "Starting API on http://$($ApiHost):$ApiPort"
$apiJob = Start-Job -ScriptBlock {
    param($Python, $ApiHost, $ApiPort, $AppDir)
    & $Python -m uvicorn app.api:app --host $ApiHost --port $ApiPort --app-dir $AppDir
} -ArgumentList $PythonPath, $ApiHost, $ApiPort, $AppDir

if (-not (Test-Http200 "http://$($ApiHost):$ApiPort/health" 40)) {
    Write-Err "API failed to become healthy"
    Receive-Job $apiJob -Keep | Out-String | Write-Host
    exit 1
}
Write-Ok "API is healthy"

$streamlitJob = $null
if (-not $NoStreamlit) {
    Write-Info "Starting Streamlit on http://localhost:$StreamlitPort"
    $streamlitJob = Start-Job -ScriptBlock {
        param($Python, $AppPath, $Port)
        Start-Sleep -Seconds 2
        & $Python -m streamlit run $AppPath --server.port $Port --server.headless true
    } -ArgumentList $PythonPath, $StreamlitApp, $StreamlitPort

    if (-not (Test-Http200 "http://localhost:$StreamlitPort" 30)) {
        Write-Warn "Streamlit not reachable on port $StreamlitPort"
    } else { Write-Ok "Streamlit is up" }
}

$reactJob = $null
if (-not $NoReact) {
    Write-Info "Starting React (Vite) on http://localhost:$VitePort"
    $reactJob = Start-Job -ScriptBlock {
        param($Dir, $Port)
        Push-Location $Dir
        try {
            $env:PORT = "$Port"
            npm run dev | Write-Output
        } finally { Pop-Location }
    } -ArgumentList $WebDir, $VitePort

    $viteOk = (Test-Http200 "http://localhost:$VitePort" 25) -or (Test-Http200 "http://localhost:5174" 5) -or (Test-Http200 "http://localhost:5175" 5)
    if ($viteOk) { Write-Ok "React dev server is up" } else { Write-Warn "React dev server not responding yet" }
}

if ($OpenBrowser) {
    if (-not $NoReact) { Start-Process "http://localhost:$VitePort" }
    if (-not $NoStreamlit) { Start-Process "http://localhost:$StreamlitPort" }
    Start-Process "http://$($ApiHost):$ApiPort/docs"
}

if ($RunDemo) {
    Write-Info "Running demo script"
    & $PythonPath (Join-Path $AppDir 'demo\run_demo.py')
}

Write-Ok "All tasks dispatched. Use Get-Job to inspect background jobs."
