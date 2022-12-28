# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 09:24:38 2022

@author: ricar
"""

from pdf2image import convert_from_path
from glob import glob
from os.path import join, basename, splitext

nubanks = (

    glob(r'C:\projeto_faturas\faturas\pdfs\Nubank_*.pdf')
    
)

for nubank in nubanks: 

    arquivo = splitext(basename(nubank))[0]
    destino = join(r'C:\projeto_faturas\faturas\imagens', arquivo + '.jpg')

    pages = convert_from_path(nubank, 500)
    
    for page in pages:
        pass
    
    page.save(destino, 'JPEG')
    

ceees = (

    glob(r'C:\projeto_faturas\faturas\pdfs\CEEE_*.pdf')
    
)

for ceee in ceees: 

    arquivo = splitext(basename(ceee))[0]
    destino = join(r'C:\projeto_faturas\faturas\imagens', arquivo + '.jpg')

    pages = convert_from_path(ceee, 500)
    
    for page in pages:
        break
    
    page.save(destino, 'JPEG')