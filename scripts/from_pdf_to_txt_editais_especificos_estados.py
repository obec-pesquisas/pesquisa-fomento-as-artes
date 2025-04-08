#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 17:18:04 2025

Transformação de arquivos pdf em arquivo de texto com formatação markdown.

Não funcionou: truncou o pdf, e não conseguiu extrair o texto de forma
eficiente.

gemini-2.0-flah-001: trunca o texto.

@author: gilberto
"""

##########################################################
# configuração inicial

from google import genai
import numpy as np
import os
import pandas as pd
import random
from PyPDF2 import PdfReader, PdfWriter
import time

MODEL = "gemini-2.0-flash-001"
client = genai.Client(api_key="AIzaSyBwsQ0AGOKVcmxSekEcNoBNRc1zfjH2Zo0")

def ask_gemini(pergunta, edital, max_tentativas=5):
    """
    Send a request to API Gemini.

    Parameters
    ----------
    pergunta : str
        A descriptive question fo ask gemini.
    edital: list
        Pdf file.
    max_tentativas : int, optional
        Number of trials in the exponential backoff. The default is 5.

    Returns
    -------
    str
        String with the markdown table.

    """
    filename = 'documentos/editais-especificos-apenas-estados/' + edital
    reader = PdfReader(filename)
    limites_grupo = list(np.arange(0, len(reader.pages), 3)) + [len(reader.pages)]
    limites_grupo.pop(0)
    grupo = 0
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        writer.add_page(page)
        if (i + 1) >= limites_grupo[grupo]:
            # print(f'{i+1}= | {grupo=}')
            output_path = f"doc_{grupo+1}.pdf"
            with open(output_path, "wb") as output_pdf:
                writer.write(output_pdf)
            grupo += 1
            writer = PdfWriter()
                
    docs = []
    for i in range(grupo):
        print(f"Parte {i+1} de {edital}.")
        tentativa = 0
        while tentativa < max_tentativas:
            try:
                pdfs = [client.files.upload(file=f"doc_{i+1}.pdf", config=dict(mime_type='application/pdf'))]
                pdfs.append(pergunta)
                
                response = client.models.generate_content(
                    model=MODEL,
                    contents=pdfs
                )
                if not response.text:
                    raise ValueError("AI haven't responded yet.")
                else:
                    docs.append(response.text)
                    break
            except:
                tentativa += 1
                tempo_espera = (2 ** tentativa) + random.random()
                print(f"Limite de taxa atingido. Esperando {tempo_espera:.2f} segundos...")
                time.sleep(tempo_espera)
        if tentativa == max_tentativas:
            print(f"Não foi possível ler {edital}.")
            return None
    for i in range(grupo):
        os.remove(f"doc_{i+1}.pdf")
   
    texto = "\n\n".join(docs)
    texto = texto.replace("```markdown", "\n")
    texto = texto.replace("```", "\n")  
    return texto

################################################
# chamando a ia

pergunta = """Você é um especialista em extração e formatação de texto de documentos PDF. Sua tarefa é analisar o seguinte documento PDF e converter seu conteúdo textual para o formato Markdown.

Instruções:

1.  **Extração Completa:**
    * Extraia TODO o texto do documento PDF, incluindo todas as páginas.
    * Não omita nenhuma informação ou página.
    * Não trunque o documento. O texto da resposta deve conter todo o texto do documento original.
2.  **Formatação Markdown:**
    * Formate o texto extraído usando a sintaxe Markdown.
    * Mantenha a estrutura e a organização do texto original o máximo possível.
    * Sempre que possível, utilize cabeçalhos, listas, tabelas e outros elementos Markdown para melhorar a legibilidade.
3.  **Elementos Complexos:**
    * Tente converter tabelas para o formato Markdown de tabelas.
    * Caso existam imagens no pdf, indique no texto markdown onde elas se encontram. Em sua indicação, use o texto "<!-- imagem -->".
    * Caso fórmulas matemáticas estejam presentes, as mantenha da forma mais fiel possível, se necessário, as transcreva utilizando LaTex.
4.  **Verificação de erros:**
    * Verifique se todo o texto do PDF foi corretamente transcrito, comparando o texto do PDF com o texto da sua resposta.
    * Caso encontre erros, os corrija.
5.  **Entrega:**
    * Forneça o texto completo formatado em Markdown como sua resposta.

"""

output_dir = 'dados/processados/editais_especificos_estados_texto'

files = sorted(os.listdir('documentos/editais-especificos-apenas-estados/'))
df_files = pd.DataFrame({
        "files": files
    })

for i in range(204, df_files.shape[0]):
    edital = df_files.iat[i, 0]
    print(f'{i=} | {edital}')
    
    resposta = ask_gemini(pergunta, edital, max_tentativas=10)
    
    with open(f'{output_dir}/{edital.strip(".pdf")}.txt', 'w') as saida:
        saida.write(resposta)