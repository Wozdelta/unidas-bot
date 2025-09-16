#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar o relatório diário do bot Unidas
Execute este arquivo para ver como será o relatório
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

from monitor_bot import BotMonitorUnidas

def testar_relatorio():
    """Testar o envio do relatório diário"""
    print("TESTANDO RELATORIO DIARIO...")
    print("=" * 50)
    
    # Criar instância do bot
    bot = BotMonitorUnidas()
    
    # Simular algumas estatísticas para teste
    bot.estatisticas = {
        'data': '2025-09-15',
        'tentativas': 25,
        'carros_encontrados': 2,
        'notificacoes_enviadas': 2,
        'erros': 1,
        'ultimo_carro_encontrado': '2025-09-15 14:30:00'
    }
    
    print("Estatisticas simuladas:")
    print(f"   Tentativas: {bot.estatisticas['tentativas']}")
    print(f"   Carros encontrados: {bot.estatisticas['carros_encontrados']}")
    print(f"   Notificacoes enviadas: {bot.estatisticas['notificacoes_enviadas']}")
    print(f"   Erros: {bot.estatisticas['erros']}")
    print(f"   Ultimo carro: {bot.estatisticas['ultimo_carro_encontrado']}")
    print()
    
    # Testar o relatório
    print("Enviando relatorio de teste...")
    bot.enviar_relatorio_diario()
    
    print()
    print("Teste concluido!")
    print("Verifique seu WhatsApp para ver a mensagem")
    print("Ou verifique o arquivo 'notificacoes.txt' se houver falha")

if __name__ == "__main__":
    testar_relatorio()
