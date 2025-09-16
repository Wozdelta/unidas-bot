@echo off
echo ========================================
echo  Bot de Monitoramento Unidas - Setup
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado!
    echo.
    echo Por favor, instale o Python primeiro:
    echo 1. Vá para https://python.org/downloads/
    echo 2. Baixe a versão mais recente do Python
    echo 3. Durante a instalação, marque "Add Python to PATH"
    echo 4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado!
python --version

echo.
echo Instalando dependências...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha na instalação das dependências!
    echo Tente executar manualmente:
    echo python -m pip install selenium webdriver-manager requests schedule python-dotenv pywhatkit
    pause
    exit /b 1
)

echo.
echo [OK] Dependências instaladas com sucesso!
echo.
echo Criando arquivo de configuração...
if not exist .env (
    copy .env.example .env
    echo [OK] Arquivo .env criado!
    echo.
    echo IMPORTANTE: Edite o arquivo .env e adicione seu número do WhatsApp
    echo Exemplo: WHATSAPP_PHONE_NUMBER=+5511999999999
) else (
    echo [OK] Arquivo .env já existe
)

echo.
echo ========================================
echo  Setup concluído!
echo ========================================
echo.
echo Próximos passos:
echo 1. Edite o arquivo .env com seu número do WhatsApp
echo 2. Execute: python monitor_bot.py --test
echo 3. Se funcionar, execute: python monitor_bot.py
echo.
pause
