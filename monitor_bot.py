import os
import time
import logging
import schedule
import json
from datetime import datetime, timedelta
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
        self.arquivo_estatisticas = 'estatisticas_bot.json'
        self.carregar_estatisticas()
        
    def verificar_e_notificar(self):
        """Função principal de monitoramento"""
        try:
            logger.info("Iniciando verificação de disponibilidade de carros...")
            
            # Executar o scraper
            resultado = self.scraper.executar_verificacao()
            
            if resultado.get('disponivel', False):
                logger.info("Carros disponíveis! Preparando notificação...")
                self.atualizar_estatisticas('carro_encontrado')
                
                # Verificar intervalo para evitar spam
                horario_atual = datetime.now()
                if (self.ultimo_horario_notificacao is None or 
                    (horario_atual - self.ultimo_horario_notificacao).seconds > self.intervalo_notificacao):
                    
                    # Enviar notificação WhatsApp
                    sucesso = self.notificador_whatsapp.enviar_notificacao_disponibilidade_carro(resultado)
                    
                    if sucesso:
                        logger.info("Notificação WhatsApp enviada com sucesso")
                        self.atualizar_estatisticas('notificacao_enviada')
                        self.ultimo_horario_notificacao = horario_atual
                    else:
                        logger.warning("Notificação WhatsApp falhou, tentando alternativas...")
                        
                        # Tentar métodos alternativos de notificação
                        mensagem = f"🚗 Carro disponível na Unidas! Categoria: {', '.join(resultado.get('veiculos', []))}. Datas: 26/12 às 08:00 até 03/01 às 12:00. Retirada no Aeroporto de Ribeirão Preto."
                        
                        # Notificação desktop
                        NotificadorAlternativo.criar_notificacao_desktop(mensagem)
                        
                        # Salvar em arquivo
                        NotificadorAlternativo.salvar_em_arquivo(mensagem)
                        
                        self.atualizar_estatisticas('notificacao_enviada')
                        self.ultimo_horario_notificacao = horario_atual
                else:
                    logger.info(f"Intervalo de notificação ativo. Última notificação: {self.ultimo_horario_notificacao}")
            else:
                logger.info("Nenhum carro disponível no momento")
                
        except Exception as e:
            logger.error(f"Erro em verificar_e_notificar: {str(e)}")
            self.atualizar_estatisticas('erro')
        
        # Sempre atualizar estatísticas
        self.atualizar_estatisticas('tentativa')
    
    def iniciar_monitoramento(self):
        """Iniciar o agendamento de monitoramento"""
        logger.info("Iniciando bot de monitoramento de carros Unidas...")
        logger.info("Critérios de monitoramento:")
        logger.info("- Data de retirada: 26/12/2025 às 08:00")
        logger.info("- Data de devolução: 03/01/2026 às 12:00")
        logger.info("- Local: Aeroporto de Ribeirão Preto, Ribeirão Preto - SP")
        logger.info("- Categoria: SUV 4 portas, Minivan 7 lugares, Chevrolet Spin, Fiat Doblo")
        logger.info("- Verificação: a cada 30 minutos")
        logger.info("- Relatório: a cada 1 hora")
        
        # Agendar o trabalho a cada 30 minutos
        schedule.every(30).minutes.do(self.verificar_e_notificar)
        
        # Agendar relatório a cada 1 hora
        schedule.every().hour.do(self.enviar_relatorio_horario)
        
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
    
    def carregar_estatisticas(self):
        """Carregar estatísticas do arquivo JSON"""
        try:
            if os.path.exists(self.arquivo_estatisticas):
                with open(self.arquivo_estatisticas, 'r', encoding='utf-8') as f:
                    self.estatisticas = json.load(f)
            else:
                self.resetar_estatisticas_diarias()
        except Exception as e:
            logger.error(f"Erro ao carregar estatísticas: {e}")
            self.resetar_estatisticas_diarias()
    
    def resetar_estatisticas_diarias(self):
        """Resetar estatísticas para um novo dia"""
        self.estatisticas = {
            'data': datetime.now().strftime('%Y-%m-%d'),
            'tentativas': 0,
            'carros_encontrados': 0,
            'notificacoes_enviadas': 0,
            'erros': 0,
            'ultimo_carro_encontrado': None
        }
        self.salvar_estatisticas()
    
    def atualizar_estatisticas(self, tipo, dados=None):
        """Atualizar estatísticas baseado no tipo de evento"""
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        # Se mudou o dia, resetar estatísticas
        if self.estatisticas.get('data') != data_hoje:
            self.resetar_estatisticas_diarias()
        
        if tipo == 'tentativa':
            self.estatisticas['tentativas'] += 1
        elif tipo == 'carro_encontrado':
            self.estatisticas['carros_encontrados'] += 1
            self.estatisticas['ultimo_carro_encontrado'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif tipo == 'notificacao_enviada':
            self.estatisticas['notificacoes_enviadas'] += 1
        elif tipo == 'erro':
            self.estatisticas['erros'] += 1
        
        self.salvar_estatisticas()
    
    def salvar_estatisticas(self):
        """Salvar estatísticas no arquivo JSON"""
        try:
            with open(self.arquivo_estatisticas, 'w', encoding='utf-8') as f:
                json.dump(self.estatisticas, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas: {e}")
    
    def enviar_relatorio_horario(self):
        """Enviar relatório a cada 1 hora"""
        try:
            logger.info("Gerando relatório horário...")
            
            hora_atual = datetime.now().strftime('%H:%M')
            data_atual = datetime.now().strftime('%d/%m/%Y')
            
            # Preparar mensagem do relatório
            mensagem = f"📊 *RELATÓRIO HORÁRIO - UNIDAS BOT*\n"
            mensagem += f"📅 Data: {data_atual} - {hora_atual}\n\n"
            mensagem += f"🔍 Tentativas hoje: {self.estatisticas.get('tentativas', 0)}\n"
            mensagem += f"🚗 Carros encontrados hoje: {self.estatisticas.get('carros_encontrados', 0)}\n"
            mensagem += f"📱 Notificações enviadas: {self.estatisticas.get('notificacoes_enviadas', 0)}\n"
            mensagem += f"❌ Erros ocorridos: {self.estatisticas.get('erros', 0)}\n\n"
            
            if self.estatisticas.get('ultimo_carro_encontrado'):
                mensagem += f"🕐 Último carro encontrado: {self.estatisticas.get('ultimo_carro_encontrado')}\n\n"
            else:
                mensagem += f"ℹ️ Nenhum carro encontrado hoje\n\n"
            
            mensagem += f"🔄 Bot funcionando normalmente\n"
            mensagem += f"⏰ Próxima verificação: a cada 30 minutos\n"
            mensagem += f"📈 Próximo relatório: em 1 hora"
            
            # Enviar relatório via WhatsApp
            sucesso = self.notificador_whatsapp.enviar_mensagem_personalizada(mensagem)
            
            if sucesso:
                logger.info("Relatório horário enviado com sucesso")
            else:
                logger.warning("Falha ao enviar relatório horário via WhatsApp")
                # Salvar em arquivo como backup
                NotificadorAlternativo.salvar_em_arquivo(f"RELATÓRIO HORÁRIO: {mensagem}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatório horário: {str(e)}")
    
    def enviar_relatorio_diario(self):
        """Enviar relatório diário às 1h da manhã (mantido para compatibilidade)"""
        try:
            logger.info("Gerando relatório diário...")
            
            data_ontem = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
            
            # Preparar mensagem do relatório
            mensagem = f"📊 *RELATÓRIO DIÁRIO - UNIDAS BOT*\n"
            mensagem += f"📅 Data: {data_ontem}\n\n"
            mensagem += f"🔍 Tentativas de verificação: {self.estatisticas.get('tentativas', 0)}\n"
            mensagem += f"🚗 Carros disponíveis encontrados: {self.estatisticas.get('carros_encontrados', 0)}\n"
            mensagem += f"📱 Notificações enviadas: {self.estatisticas.get('notificacoes_enviadas', 0)}\n"
            mensagem += f"❌ Erros ocorridos: {self.estatisticas.get('erros', 0)}\n\n"
            
            if self.estatisticas.get('ultimo_carro_encontrado'):
                mensagem += f"🕐 Último carro encontrado: {self.estatisticas.get('ultimo_carro_encontrado')}\n\n"
            else:
                mensagem += f"ℹ️ Nenhum carro foi encontrado ontem\n\n"
            
            mensagem += f"🔄 Bot funcionando normalmente\n"
            mensagem += f"⏰ Próxima verificação: a cada 30 minutos"
            
            # Enviar relatório via WhatsApp
            sucesso = self.notificador_whatsapp.enviar_mensagem_personalizada(mensagem)
            
            if sucesso:
                logger.info("Relatório diário enviado com sucesso")
            else:
                logger.warning("Falha ao enviar relatório diário via WhatsApp")
                # Salvar em arquivo como backup
                NotificadorAlternativo.salvar_em_arquivo(f"RELATÓRIO DIÁRIO: {mensagem}")
            
            # Resetar estatísticas para o novo dia
            self.resetar_estatisticas_diarias()
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatório diário: {str(e)}")

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
