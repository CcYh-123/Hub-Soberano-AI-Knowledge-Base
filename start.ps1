<#
.SYNOPSIS
Script de arranque para el Sistema SaaS Universal.
.DESCRIPTION
Activa el entorno virtual y ejecuta la aplicacion principal.
#>

$ErrorActionPreference = "Stop"

# Directorio base del script
$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $baseDir

Write-Host "Iniciando Sistema Universal SaaS..." -ForegroundColor Cyan

# Comprobar si existe el entorno virtual
if (-Not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] El entorno virtual '.venv' no fue encontrado." -ForegroundColor Red
    Write-Host "Si es la primera vez, asegurate de ejecutar la instalacion de dependencias." -ForegroundColor Yellow
    Pause
    exit
}

# Activar entorno y ejecutar
. .\.venv\Scripts\Activate.ps1
python main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] La aplicacion se cerro de forma inesperada." -ForegroundColor Red
    Pause
}
