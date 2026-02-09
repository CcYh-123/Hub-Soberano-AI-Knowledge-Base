@ECHO OFF
REM ===============================================================================
REM                    ANTIGRAVITY - LANZADOR DE AUTOMATIZACIÓN
REM                              antigravity_run.bat
REM                               DIRECTIVA: D008
REM ===============================================================================
REM Este archivo es el punto de entrada para Windows Task Scheduler.
REM Ejecuta el ciclo completo de Antigravity de forma autónoma.
REM ===============================================================================

TITLE Antigravity - Ejecucion Automatica

REM Cambiar al directorio del proyecto
cd /d "C:\Users\Lenovo\Antigravity_Home\Proyecto_Antigravity"

ECHO.
ECHO ===============================================================================
ECHO     ANTIGRAVITY - SISTEMA DE AUTOMATIZACION (D008)
ECHO ===============================================================================
ECHO.
ECHO [%DATE% %TIME%] Iniciando ejecucion automatica...
ECHO.

REM Paso 1: Ejecutar indexador para validar mapa (Auto-Diagnostico)
ECHO [PASO 1/3] Ejecutando Indexador (D001)...
py scripts/script_001_indexador.py
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Indexador fallo con codigo: %ERRORLEVEL%
    ECHO [ERROR] Abortando mision automatica.
    EXIT /B 1
)
ECHO [OK] Indexador completado.
ECHO.

REM Paso 2: Ejecutar orquestador principal
ECHO [PASO 2/3] Ejecutando Orquestador Principal (D006)...
py main.py
SET MAIN_EXIT_CODE=%ERRORLEVEL%
IF %MAIN_EXIT_CODE% NEQ 0 (
    ECHO [WARNING] Orquestador retorno codigo: %MAIN_EXIT_CODE%
) ELSE (
    ECHO [OK] Orquestador completado exitosamente.
)
ECHO.

REM Paso 3: Ejecutar heartbeat para validar ejecución
ECHO [PASO 3/3] Ejecutando Heartbeat (D008)...
py scripts/heartbeat_skill.py
IF %ERRORLEVEL% NEQ 0 (
    ECHO [WARNING] Heartbeat detecto problemas.
) ELSE (
    ECHO [OK] Heartbeat confirma sistema saludable.
)

ECHO.
ECHO ===============================================================================
ECHO [%DATE% %TIME%] Mision automatica finalizada.
ECHO ===============================================================================
ECHO.

REM Salir con el código del orquestador principal
EXIT /B %MAIN_EXIT_CODE%
