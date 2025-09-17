import os
import time
import logging
import platform
import glob
import subprocess
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unidas_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnidasScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def configurar_driver(self):
        # Configurar opções do Chrome para ambiente headless
        opcoes_chrome = Options()
        opcoes_chrome.add_argument('--headless')
        opcoes_chrome.add_argument('--no-sandbox')
        opcoes_chrome.add_argument('--disable-dev-shm-usage')
        opcoes_chrome.add_argument('--disable-gpu')
        opcoes_chrome.add_argument('--window-size=1920,1080')
        opcoes_chrome.add_argument('--disable-extensions')
        opcoes_chrome.add_argument('--disable-plugins')
        opcoes_chrome.add_argument('--disable-images')
        opcoes_chrome.add_argument('--remote-debugging-port=9222')
        opcoes_chrome.add_argument('--disable-web-security')
        opcoes_chrome.add_argument('--allow-running-insecure-content')
        opcoes_chrome.add_experimental_option('excludeSwitches', ['enable-logging'])
        opcoes_chrome.add_experimental_option('useAutomationExtension', False)
        
        # Detectar ambiente (Windows vs Linux)
        sistema = platform.system().lower()
        
        try:
            if sistema == 'linux':
                # Configuração para ambiente Linux (Railway/Docker)
                logger.info("Detectado ambiente Linux - configurando Chrome")
                
                # Verificar se Chrome existe antes de tentar usar
                chrome_paths = [
                    '/usr/bin/google-chrome-stable',
                    '/usr/bin/google-chrome',
                    '/usr/bin/chromium',
                    '/usr/bin/chromium-browser'
                ]
                
                # Também verificar ChromeDriver
                chromedriver_paths = [
                    '/usr/local/bin/chromedriver',
                    '/usr/bin/chromedriver',
                    '/usr/lib/chromium-browser/chromedriver'
                ]
                
                chrome_found = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_found = path
                        logger.info(f"Chrome encontrado em: {path}")
                        break
                
                # Verificar se ChromeDriver existe
                chromedriver_found = None
                for path in chromedriver_paths:
                    if os.path.exists(path):
                        chromedriver_found = path
                        logger.info(f"ChromeDriver encontrado em: {path}")
                        break
                
                if chrome_found:
                    opcoes_chrome.binary_location = chrome_found
                    try:
                        if chromedriver_found:
                            servico = Service(chromedriver_found)
                            self.driver = webdriver.Chrome(service=servico, options=opcoes_chrome)
                            logger.info(f"Chrome inicializado com ChromeDriver: {chromedriver_found}")
                        else:
                            self.driver = webdriver.Chrome(options=opcoes_chrome)
                            logger.info("Chrome inicializado com ChromeDriver padrão")
                    except Exception as e:
                        logger.error(f"Erro ao inicializar Chrome: {e}")
                        # Fallback para webdriver-manager
                        try:
                            from webdriver_manager.chrome import ChromeDriverManager
                            servico = Service(ChromeDriverManager().install())
                            opcoes_chrome.binary_location = chrome_found
                            self.driver = webdriver.Chrome(service=servico, options=opcoes_chrome)
                            logger.info("Chrome inicializado com webdriver-manager")
                        except Exception as e2:
                            logger.error(f"Erro no fallback: {e2}")
                            raise Exception("Não foi possível inicializar o navegador Chrome")
                else:
                    logger.error("Nenhum browser Chrome/Chromium encontrado no sistema")
                    # Listar arquivos para debug
                    try:
                        import subprocess
                        result = subprocess.run(['ls', '-la', '/usr/bin/'], capture_output=True, text=True)
                        logger.info(f"Conteúdo de /usr/bin/: {result.stdout[:500]}")
                    except:
                        pass
                    raise Exception("Chrome/Chromium não encontrado")
            else:
                # Configuração para Windows
                logger.info("Detectado ambiente Windows - configurando Chrome")
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    from webdriver_manager.core.os_manager import ChromeType
                    
                    servico = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
                    self.driver = webdriver.Chrome(service=servico, options=opcoes_chrome)
                except Exception as e:
                    logger.warning(f"Erro ao configurar ChromeDriverManager: {e}")
                    # Fallback: tentar Chrome padrão do sistema
                    self.driver = webdriver.Chrome(options=opcoes_chrome)
                    
        except Exception as e:
            logger.error(f"Erro ao inicializar Chrome/Chromium: {e}")
            raise Exception("Não foi possível inicializar o navegador Chrome. Verifique se o Chrome está instalado.")
        
        self.wait = WebDriverWait(self.driver, 20)
        
    def fechar_driver(self):
        """Fechar o WebDriver"""
        if self.driver:
            self.driver.quit()
            
    def preencher_formulario_busca(self):
        """Preencher o formulário de busca com os critérios especificados"""
        try:
            logger.info("Acessando site da Unidas...")
            self.driver.get("https://www.unidas.com.br/para-voce/reservas-nacionais")
            
            # Aguardar carregamento da página
            time.sleep(8)
            
            # Salvar screenshot para debug
            self.driver.save_screenshot("debug_pagina_inicial.png")
            
            # Tentar múltiplos seletores para o formulário
            seletores_formulario = [
                "form",
                "[data-testid*='search']",
                ".search-form",
                ".reservation-form",
                "#search-form"
            ]
            
            formulario_encontrado = False
            for seletor in seletores_formulario:
                try:
                    formulario = self.driver.find_element(By.CSS_SELECTOR, seletor)
                    if formulario:
                        logger.info(f"Formulário encontrado com seletor: {seletor}")
                        formulario_encontrado = True
                        break
                except:
                    continue
            
            if not formulario_encontrado:
                logger.warning("Formulário específico não encontrado, tentando campos individuais")
            
            # Tentar encontrar e preencher local de retirada com múltiplos seletores
            logger.info("Procurando campo de local de retirada...")
            seletores_local = [
                "input[placeholder*='retirada']",
                "input[placeholder*='Retirada']", 
                "input[placeholder*='origem']",
                "input[placeholder*='Origem']",
                "input[name*='pickup']",
                "input[id*='pickup']",
                "input[data-testid*='pickup']",
                "input[type='text']"
            ]
            
            campo_retirada = None
            for seletor in seletores_local:
                try:
                    elementos = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    for elemento in elementos:
                        if elemento.is_displayed() and elemento.is_enabled():
                            campo_retirada = elemento
                            logger.info(f"Campo de retirada encontrado: {seletor}")
                            break
                    if campo_retirada:
                        break
                except:
                    continue
            
            if campo_retirada:
                try:
                    campo_retirada.click()
                    campo_retirada.clear()
                    campo_retirada.send_keys("Ribeirão Preto")
                    time.sleep(3)
                    
                    # Procurar opções no dropdown
                    opcoes_dropdown = [
                        "//div[contains(text(), 'Ribeirão Preto')]",
                        "//li[contains(text(), 'Ribeirão Preto')]",
                        "//option[contains(text(), 'Ribeirão Preto')]",
                        "//*[contains(text(), 'Aeroporto') and contains(text(), 'Ribeirão')]"
                    ]
                    
                    for xpath in opcoes_dropdown:
                        try:
                            opcao = self.driver.find_element(By.XPATH, xpath)
                            if opcao.is_displayed():
                                opcao.click()
                                logger.info("Opção de Ribeirão Preto selecionada")
                                break
                        except:
                            continue
                            
                except Exception as e:
                    logger.warning(f"Erro ao preencher local de retirada: {e}")
            else:
                logger.warning("Campo de local de retirada não encontrado")
            
            time.sleep(3)
            
            # Procurar e preencher datas
            logger.info("Procurando campos de data...")
            campos_data = self.driver.find_elements(By.CSS_SELECTOR, "input[type='date'], input[placeholder*='data'], input[name*='date']")
            
            if len(campos_data) >= 2:
                try:
                    # Data de retirada
                    campos_data[0].clear()
                    campos_data[0].send_keys("2025-12-26")
                    logger.info("Data de retirada preenchida")
                    
                    # Data de devolução  
                    campos_data[1].clear()
                    campos_data[1].send_keys("2026-01-03")
                    logger.info("Data de devolução preenchida")
                except Exception as e:
                    logger.warning(f"Erro ao preencher datas: {e}")
            
            time.sleep(2)
            
            # Procurar botão de busca
            logger.info("Procurando botão de busca...")
            seletores_botao = [
                "button[type='submit']",
                "button[class*='search']",
                "button[class*='buscar']",
                "input[type='submit']",
                "button:contains('Buscar')",
                "button:contains('Pesquisar')",
                "[data-testid*='search']"
            ]
            
            botao_encontrado = False
            for seletor in seletores_botao:
                try:
                    botoes = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    for botao in botoes:
                        if botao.is_displayed() and botao.is_enabled():
                            botao.click()
                            logger.info(f"Botão de busca clicado: {seletor}")
                            botao_encontrado = True
                            break
                    if botao_encontrado:
                        break
                except:
                    continue
            
            if not botao_encontrado:
                logger.warning("Botão de busca não encontrado, tentando Enter")
                try:
                    from selenium.webdriver.common.keys import Keys
                    if campo_retirada:
                        campo_retirada.send_keys(Keys.RETURN)
                except:
                    pass
            
            # Aguardar carregamento dos resultados
            logger.info("Aguardando carregamento dos resultados...")
            time.sleep(15)
            
            # Salvar screenshot dos resultados
            self.driver.save_screenshot("debug_resultados.png")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao preencher formulário de busca: {str(e)}")
            # Salvar screenshot do erro
            try:
                self.driver.save_screenshot("debug_erro.png")
            except:
                pass
            return False
    
    def verificar_disponibilidade_carros(self):
        """Verificar disponibilidade de SUV ou Minivan"""
        try:
            logger.info("Verificando disponibilidade de carros...")
            
            # Aguardar carregamento dos resultados
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Procurar categorias de carros - tentar múltiplos seletores
            seletores_carros = [
                "div[class*='car'], div[class*='vehicle'], div[class*='categoria']",
                ".car-item, .vehicle-item, .categoria-item",
                "[data-category], [data-car-type]",
                "div:contains('SUV'), div:contains('Minivan'), div:contains('Utilitário')"
            ]
            
            carros_disponiveis = []
            
            for seletor in seletores_carros:
                try:
                    carros = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    if carros:
                        logger.info(f"Encontrados {len(carros)} elementos de carro com seletor: {seletor}")
                        break
                except:
                    continue
            
            # Se nenhum elemento específico de carro foi encontrado, verificar conteúdo da página
            conteudo_pagina = self.driver.page_source.lower()
            
            # Verificar palavras-chave de SUV ou Minivan
            palavras_suv = [
                'suv', 'utilitário', 'minivan', 'van', 'sw5', 'sw7', 
                'jeep', 'compass', 'renegade', 'ecosport', 'duster',
                'carro minivan', 'minivan 7 lugares', '7 lugares',
                'chevrolet spin', 'spin', 'fiat doblo', 'doblo',
                'grupo i', 'categoria i'
            ]
            
            veiculos_encontrados = []
            for palavra in palavras_suv:
                if palavra in conteudo_pagina:
                    veiculos_encontrados.append(palavra)
            
            # Verificar se há veículos disponíveis
            if veiculos_encontrados:
                logger.info(f"Possíveis veículos encontrados: {veiculos_encontrados}")
                
                # Verificar se não está esgotado/indisponível - buscar próximo ao veículo encontrado
                palavras_indisponivel = ['esgotado', 'indisponível', 'não disponível', 'sem estoque', 'sold out']
                esta_disponivel = True
                
                # Verificar contexto específico para cada veículo encontrado
                for veiculo in veiculos_encontrados:
                    # Encontrar a posição do veículo no texto
                    pos_veiculo = conteudo_pagina.find(veiculo)
                    if pos_veiculo != -1:
                        # Verificar texto ao redor do veículo (500 caracteres antes e depois)
                        inicio = max(0, pos_veiculo - 500)
                        fim = min(len(conteudo_pagina), pos_veiculo + 500)
                        contexto = conteudo_pagina[inicio:fim]
                        
                        # Verificar se há palavras de indisponibilidade no contexto
                        for palavra in palavras_indisponivel:
                            if palavra in contexto:
                                logger.info(f"Veículo {veiculo} encontrado mas indisponível: {palavra}")
                                esta_disponivel = False
                                break
                        
                        if not esta_disponivel:
                            break
                
                if esta_disponivel:
                    try:
                        # Tentar capturar mais detalhes sobre os veículos
                        detalhes_elementos = self.driver.find_elements(By.CSS_SELECTOR, ".vehicle-details, .car-info, .price, .disponivel")
                        detalhes = [elem.text for elem in detalhes_elementos[:3]]  # Primeiros 3 elementos
                    except:
                        detalhes = []
                
                    return {
                        'disponivel': True,
                        'veiculos': veiculos_encontrados,
                        'detalhes': f"Veículos DISPONÍVEIS encontrados: {', '.join(veiculos_encontrados)}"
                    }
                else:
                    logger.info("Veículos encontrados mas todos estão esgotados/indisponíveis")
                    return {'disponivel': False, 'veiculos': [], 'detalhes': 'Veículos encontrados mas esgotados'}
                
            # Se chegou até aqui, verificar se há alguma indicação de disponibilidade geral
            palavras_disponivel = ['disponível', 'reservar', 'selecionar', 'escolher']
            for palavra in palavras_disponivel:
                if palavra in conteudo_pagina:
                    logger.info(f"Possível disponibilidade detectada: {palavra}")
                    return {
                        'disponivel': True,
                        'veiculos': ['Veículo disponível'],
                        'detalhes': f"Disponibilidade detectada: {palavra}"
                    }
            
            # Verificar mensagens de "sem resultados" ou "indisponível"
            palavras_sem_resultado = ['não encontrado', 'indisponível', 'sem resultado', 'nenhum veículo', 'no results']
            for palavra in palavras_sem_resultado:
                if palavra in conteudo_pagina:
                    logger.info(f"Nenhuma disponibilidade detectada: {palavra}")
                    return {'disponivel': False, 'veiculos': [], 'detalhes': 'Nenhum veículo disponível'}
            
            # Se não conseguir determinar disponibilidade, salvar conteúdo da página para debug
            logger.warning("Não foi possível determinar disponibilidade. Salvando conteúdo da página para análise.")
            with open('pagina_debug.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            return {'disponivel': False, 'veiculos': [], 'detalhes': 'Não foi possível determinar disponibilidade'}
            
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade de carros: {str(e)}")
            return {'disponivel': False, 'veiculos': [], 'detalhes': f'Erro na verificação: {str(e)}'}
    
    def executar_verificacao(self):
        """Executar uma verificação completa de disponibilidade"""
        try:
            self.configurar_driver()
            
            if self.preencher_formulario_busca():
                resultado = self.verificar_disponibilidade_carros()
                logger.info(f"Resultado da verificação: {resultado}")
                return resultado
            else:
                logger.error("Falha ao preencher formulário de busca")
                return {'disponivel': False, 'veiculos': [], 'detalhes': 'Erro ao preencher formulário'}
                
        except Exception as e:
            logger.error(f"Erro em executar_verificacao: {str(e)}")
            return {'disponivel': False, 'veiculos': [], 'detalhes': f'Erro geral: {str(e)}'}
        finally:
            self.fechar_driver()

if __name__ == "__main__":
    scraper = UnidasScraper()
    resultado = scraper.executar_verificacao()
    print(f"Resultado: {resultado}")
