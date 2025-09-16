import os
import time
import schedule
import logging
from datetime import datetime
from dotenv import load_dotenv
from unidas_scraper import UnidasScraper
from whatsapp_notifier import NotificadorWhatsApp, NotificadorAlternativo

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotMonitorUnidas:
    def __init__(self):
        self.scraper = UnidasScraper()
        self.notificador_whatsapp = NotificadorWhatsApp(
            numero_telefone=os.getenv('WHATSAPP_PHONE_NUMBER')
        )
        self.ultimo_horario_notificacao = None
        self.intervalo_notificacao = 3600  # 1 hora de intervalo entre notificações
        
    def verificar_e_notificar(self):
        """Função principal de monitoramento"""
        try:
            logger.info("Iniciando verificação de disponibilidade de carros...")
            
            # Executar o scraper
            resultado = self.scraper.executar_verificacao()
            
            if resultado.get('disponivel', False):
                logger.info("Carros disponíveis! Preparando notificação...")
                
                # Verificar intervalo para evitar spam
                horario_atual = datetime.now()
                if (self.ultimo_horario_notificacao is None or 
                    (horario_atual - self.ultimo_horario_notificacao).seconds > self.intervalo_notificacao):
                    
                    # Enviar notificação WhatsApp
                    sucesso = self.notificador_whatsapp.enviar_notificacao_disponibilidade_carro(resultado)
                    
                    if sucesso:
                        logger.info("Notificação WhatsApp enviada com sucesso")
                        self.ultimo_horario_notificacao = horario_atual
                    else:
                        logger.warning("Notificação WhatsApp falhou, tentando alternativas...")
                        
                        # Tentar métodos alternativos de notificação
                        mensagem = f"🚗 Carro disponível na Unidas! Categoria: {', '.join(resultado.get('veiculos', []))}. Datas: 26/12 às 08:00 até 03/01 às 12:00. Retirada no Aeroporto de Ribeirão Preto."
                        
                        # Notificação desktop
                        NotificadorAlternativo.criar_notificacao_desktop(mensagem)
                        
                        # Salvar em arquivo
                        NotificadorAlternativo.salvar_em_arquivo(mensagem)
                        
                        self.ultimo_horario_notificacao = horario_atual
                else:
                    logger.info(f"Intervalo de notificação ativo. Última notificação: {self.ultimo_horario_notificacao}")
            else:
                logger.info("Nenhum carro disponível no momento")
                
        except Exception as e:
            logger.error(f"Erro em verificar_e_notificar: {str(e)}")
    
    def iniciar_monitoramento(self):
        """Iniciar o agendamento de monitoramento"""
        logger.info("Iniciando bot de monitoramento de carros Unidas...")
        logger.info("Critérios de monitoramento:")
        logger.info("- Data de retirada: 26/12/2025 às 08:00")
        logger.info("- Data de devolução: 03/01/2026 às 12:00")
        logger.info("- Local: Aeroporto de Ribeirão Preto, Ribeirão Preto - SP")
        logger.info("- Categoria: SUV 4 portas ou Minivan")
        logger.info("- Verificação: a cada 30 minutos")
        
        # Agendar o trabalho a cada 30 minutos
        schedule.every(30).minutes.do(self.verificar_e_notificar)
        
        # Executar verificação inicial
        self.verificar_e_notificar()
        
        # Manter o bot em execução
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto por trabalhos agendados
    
    def executar_verificacao_unica(self):
        """Executar uma única verificação (para teste)"""
        logger.info("Executando verificação única de disponibilidade...")
        self.verificar_e_notificar()

def main():
    """Função principal"""
    import sys
    
    bot = BotMonitorUnidas()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Executar teste único
        bot.executar_verificacao_unica()
    else:
        # Iniciar monitoramento contínuo
        try:
            bot.iniciar_monitoramento()
        except KeyboardInterrupt:
            logger.info("Monitoramento interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Monitoramento interrompido devido a erro: {str(e)}")

if __name__ == "__main__":
    main()
