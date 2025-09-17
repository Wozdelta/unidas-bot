#!/usr/bin/env python3
import sys
import time
import os

print("🚀 TESTE SIMPLES - CONTAINER INICIADO")
print(f"🐍 Python version: {sys.version}")
print(f"🐧 OS: {os.name}")
print(f"📁 Working directory: {os.getcwd()}")
print(f"📋 Files in directory: {os.listdir('.')}")

# Verificar variáveis de ambiente
print(f"🔧 DOCKER_CONTAINER: {os.getenv('DOCKER_CONTAINER')}")
print(f"📱 WHATSAPP_PHONE_NUMBER: {os.getenv('WHATSAPP_PHONE_NUMBER')}")

# Testar imports básicos
try:
    print("📦 Testando imports...")
    import selenium
    print(f"✅ Selenium: {selenium.__version__}")
    
    import schedule
    print("✅ Schedule: OK")
    
    import requests
    print(f"✅ Requests: {requests.__version__}")
    
    from dotenv import load_dotenv
    print("✅ Python-dotenv: OK")
    
except Exception as e:
    print(f"❌ Erro no import: {e}")

# Manter container ativo
print("🔄 Container ativo - aguardando...")
for i in range(60):
    print(f"⏰ Heartbeat {i+1}/60")
    time.sleep(10)

print("✅ Teste concluído!")
