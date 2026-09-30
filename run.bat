@echo off
setlocal enabledelayedexpansion
title Purble Bakery - Windows 7 Nostalgia
cd /d "%~dp0"

echo ====================================================
echo        PURBLE BAKERY - COMFY CAKES EDITION
echo ====================================================
echo.

:: 1. Localizar o interpretador Python adequado
set "PYTHON_EXE="

:: Verifica python no PATH
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
)

:: Se nao encontrou, tenta 'py'
if not defined PYTHON_EXE (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=py"
    )
)

:: Se ainda nao encontrou, tenta caminhos comuns do usuario
if not defined PYTHON_EXE (
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    )
)

if not defined PYTHON_EXE (
    echo [ERRO] Python nao foi encontrado no sistema.
    echo Por favor, instale o Python em https://www.python.org/
    pause
    exit /b 1
)

echo Usando Python: %PYTHON_EXE%
echo Verificando biblioteca Pygame...

:: 2. Testar se o Pygame ja esta instalado no Python detectado
"%PYTHON_EXE%" -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Pygame nao encontrado. Instalando automaticamente via python -m pip...
    "%PYTHON_EXE%" -m pip install pygame
    if %errorlevel% neq 0 (
        echo.
        echo [AVISO] Tentando instalar com permissao de usuario...
        "%PYTHON_EXE%" -m pip install --user pygame
    )
)

echo.
echo Iniciando o jogo em modo janela...
"%PYTHON_EXE%" main.py

if %errorlevel% neq 0 (
    echo.
    echo O jogo encerrou com codigo de erro %errorlevel%.
    pause
)
