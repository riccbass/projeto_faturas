# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 09:24:38 2022

@author: ricar
"""

from pdf2image import convert_from_path
from glob import glob
from os.path import join, basename, splitext

from datetime import datetime
import pandas as pd

import PyPDF2 


ceees = (

    glob(r'C:\projeto_faturas\faturas\pdfs\CEEE_*24145947.pdf')
    
)

lista_consumo = []

for ceee in ceees: 

    # creating a pdf reader object 
    pdfReader = PyPDF2.PdfFileReader(ceee) 
    
    
    # creating a page object 
    pageObj = pdfReader.getPage(0) 
    
    # extracting text from page 
    text = pageObj.extractText()
    
    fim = text.find(' kWh')
    
    consumo = text[:fim].split('\n')[-1]
    
    consumo = int(consumo.replace('.', ''))
    
    anomes = splitext(ceee)[0].split('_')[-2]

    data = pd.Timestamp(datetime.strptime(anomes, '%Y%m').date())
    
    lista_consumo.append({'DATA':data,
                          'CONSUMO':consumo})
    
df = pd.DataFrame(lista_consumo)

df.to_excel(r'C:\projeto_faturas\consumo_praia.xlsx',
            sheet_name = 'BASE',
            index=False)