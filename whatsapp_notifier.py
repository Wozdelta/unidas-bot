import logging
import time
import webbrowser
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificadorWhatsApp:
    def __init__(self, numero_telefone=None):
        """
        Inicializar notificador WhatsApp
        numero_telefone: Seu número de telefone no formato internacional (ex: +5511999999999)
        """
        self.numero_telefone = numero_telefone
        
    def enviar_notificacao(self, mensagem, numero_telefone=None):
        """
        Enviar notificação WhatsApp usando web.whatsapp.com
        """
        try:
            telefone_destino = numero_telefone or self.numero_telefone
            
            if not telefone_destino:
                logger.error("Nenhum número de telefone fornecido para notificação WhatsApp")
                return False
            
            # Limpar número de telefone (remover espaços, traços, etc.)
            telefone_limpo = ''.join(filter(str.isdigit, telefone_destino.replace('+', '')))
            
            # Codificar mensagem para URL
            mensagem_codificada = urllib.parse.quote(mensagem)
            
            # Criar URL do WhatsApp Web
            url_whatsapp = f"https://web.whatsapp.com/send?phone={telefone_limpo}&text={mensagem_codificada}"
            
            logger.info(f"Abrindo WhatsApp Web para enviar mensagem para {telefone_destino}")
            logger.info(f"Mensagem: {mensagem}")
            
            # Abrir WhatsApp Web no navegador padrão
            webbrowser.open(url_whatsapp)
            
            # Também registrar a mensagem para envio manual se necessário
            self._registrar_mensagem_para_envio_manual(mensagem, telefone_destino)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação WhatsApp: {str(e)}")
            return False
    
    def _registrar_mensagem_para_envio_manual(self, mensagem, numero_telefone):
        """Registrar detalhes da mensagem para envio manual se o método automatizado falhar"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entrada_log = f"""
=== MENSAGEM WHATSAPP PARA ENVIAR ===
Horário: {timestamp}
Telefone: {numero_telefone}
Mensagem: {mensagem}
====================================
"""
        
        # Escrever em arquivo separado para referência manual
        with open('mensagens_whatsapp.log', 'a', encoding='utf-8') as f:
            f.write(entrada_log)
        
        logger.info("Mensagem registrada para envio manual se necessário")
    
    def enviar_notificacao_disponibilidade_carro(self, resultado_disponibilidade):
        """
        Enviar notificação específica para disponibilidade de carro
        """
        if resultado_disponibilidade.get('disponivel', False):
            veiculos = resultado_disponibilidade.get('veiculos', [])
            detalhes = resultado_disponibilidade.get('detalhes', '')
            
            # Criar a mensagem de notificação
            mensagem = f"""🚗 Carro disponível na Unidas! 

Categoria: {', '.join(veiculos) if veiculos else 'SUV/Minivan'}
Datas: 26/12 às 08:00 até 03/01 às 12:00
Retirada: Aeroporto de Ribeirão Preto

Detalhes: {detalhes}

Link: https://www.unidas.com.br/para-voce/reservas-nacionais

⚡ Verificação automática - {datetime.now().strftime('%d/%m/%Y %H:%M')}"""
            
            return self.enviar_notificacao(mensagem)
        
        return False
    
    def enviar_mensagem_personalizada(self, mensagem):
        """
        Enviar uma mensagem personalizada via WhatsApp
        """
        return self.enviar_notificacao(mensagem)

# Métodos alternativos de notificação para backup
class NotificadorAlternativo:
    @staticmethod
    def criar_notificacao_desktop(mensagem):
        """Criar uma notificação desktop como backup"""
        try:
            import plyer
            plyer.notification.notify(
                title="Unidas - Carro Disponível!",
                message=mensagem,
                timeout=10
            )
            return True
        except ImportError:
            logger.warning("plyer não instalado - notificações desktop não disponíveis")
            return False
        except Exception as e:
            logger.error(f"Erro ao criar notificação desktop: {str(e)}")
            return False
    
    @staticmethod
    def salvar_em_arquivo(mensagem):
        """Salvar notificação em arquivo como último recurso"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('notificacoes.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {mensagem}\n\n")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar notificação em arquivo: {str(e)}")
            return False

if __name__ == "__main__":
    # Testar o notificador
    notificador = NotificadorWhatsApp()
    
    # Mensagem de teste
    resultado_teste = {
        'disponivel': True,
        'veiculos': ['SUV', 'Minivan'],
        'detalhes': 'Teste do sistema de monitoramento'
    }
    
    notificador.enviar_notificacao_disponibilidade_carro(resultado_teste)
