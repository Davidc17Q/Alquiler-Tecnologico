# Reinicia Django + Nginx sin quedar en 502 por IP/caché de Nginx
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

Write-Host "Reiniciando Django..." -ForegroundColor Cyan
docker compose restart django

Write-Host "Esperando que Django responda (hasta 90 s)..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 45; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/api/info/" -UseBasicParsing -TimeoutSec 3
        if ($r.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    Write-Host "Django no respondio a tiempo. Revisa: docker compose logs django --tail 50" -ForegroundColor Red
    exit 1
}

Write-Host "Reiniciando Nginx..." -ForegroundColor Cyan
docker compose restart nginx

Write-Host "Listo: http://localhost" -ForegroundColor Green
