# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 15:04:39 2022

@author: ricar
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import WebDriverWait

import re

from time import sleep
import json

from shutil import move
from os import remove

origem = r'C:\Users\ricar\Downloads\exibirFat.do.pdf'
destino = r'C:\projeto_faturas\faturas\pdfs\CEEE_{}_{}.pdf'

chrome_options = webdriver.ChromeOptions()

settings = {
       "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }

prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=chrome_options)

home = 'https://servicos.ceee.com.br/AgenciaWeb/autenticar/loginCliente.do'

driver.get(home)
driver.maximize_window()

'''
login manual (recaptcha)
'''

faturas = 'https://servicos.ceee.com.br/AgenciaWeb/consultarHistoricoPagto/consultarHistoricoPagto.do'
driver.get(faturas)

while True:
            
    paginas = driver.find_element(By.XPATH, "//td[@class='paginacao' and @align='right']")
    pagina_atual = paginas.find_element(By.TAG_NAME, "strong").text
    
    '''
    tabelinha faturas
    '''
    
    linhas = driver.find_elements(By.XPATH, "//table[@id='histFat']//tbody//tr")
    
    for linha in linhas:
        
        uc = linha.find_elements(By.TAG_NAME, "td")[0].text
        fatura = linha.find_elements(By.TAG_NAME, "td")[1]
        
        mes, ano = fatura.text.split('/')
        anomes = ano + mes
        
        windows_before  = driver.current_window_handle        
        
        fatura.click()
        
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        windows_after = driver.window_handles
        new_window = [x for x in windows_after if x != windows_before][0]
        driver.switch_to.window(new_window)
                
        '''
        salvar pdf
        '''
        
        sleep(5)
        
        
        
        try:
            remove(origem)    
        except:
            pass
        
        sleep(5)
        
        driver.execute_script('window.print();')
        
        destino_aj = destino.format(anomes, uc)
        
        sleep(5)
        
        move(origem, destino_aj)

        
        driver.close()
        driver.switch_to.window(windows_before)
    
    
    print(pagina_atual)
    
    paginas_txt = paginas.text.split(' | ')
    paginas_txt = [int(pag.strip()) for pag in paginas_txt]

    pagina_seguinte = int(pagina_atual) + 1
    
    if pagina_seguinte not in paginas_txt:
        print('saíndo')
        break
    
    paginas.find_elements(By.XPATH, "//img[@align='absbottom']")[-2].click()
    
    
    



