import pandas as pd
import numpy as np
import os
import re
import time
# import vertexai
# from vertexai.generative_models import GenerativeModel
from google import genai
import random


# ================================================================================
# carregando os textos

onde_arquivos_texto = 'dados/processados/editais_especificos_estados_texto/'

arquivos = np.array(os.listdir(onde_arquivos_texto))
print(arquivos.shape)
arquivos = arquivos[np.strings.endswith(arquivos, '.txt')]
print(arquivos.shape)


textos = []
for arquivo in arquivos:
    with open(onde_arquivos_texto + arquivo) as f:
        texto = f.read()
    textos.append(texto)

ente = [arquivo.strip('.txt').split('_')[0] for arquivo in arquivos]
edital = [arquivo.strip('.txt').split('_')[-1] for arquivo in arquivos]

dados = pd.DataFrame({
    'arquivo': arquivos,
    'texto': textos,
    'ente': ente,
    'edital': edital
}, index=[arquivo.strip('.pdf') for arquivo in arquivos])

variaveis = sorted(os.listdir('documentos/prompts/'))

# lendo as informações do entes
sheet_name = 'pontos-focais' # replace with your own sheet name
sheet_id = '1T2kW7Of5YXgL40U7DObUzk_t8UGiNcOQV5jLlxg_DSE' # replace with your sheet's ID
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
informacoes_ente = pd.read_csv(url)
informacoes_ente = informacoes_ente.loc[:, ['identificacao', 'nome_ente']]
informacoes_ente['identificacao'] = informacoes_ente['identificacao'].astype(str)
informacoes_ente = informacoes_ente.rename(columns={'identificacao': 'ente'})

df_all = dados.merge(
    informacoes_ente, how='left', on='ente'
).reset_index()

df_all.sort_values(by='arquivo', inplace=True, ignore_index=True)


# editais de 2023
sheet_name = '2023' # replace with your own sheet name
sheet_id = '1U-v46gl8TylqUmNVcORcBb1pfASPT2Bw0Gg2dahJb2o' # replace with your sheet's ID
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
editais_especificos_2023 = pd.read_csv(url)
editais_especificos_2023  = editais_especificos_2023 .loc[:, ['arquivo', 'ano']]
editais_especificos_2023['arquivo'] = editais_especificos_2023['arquivo'].str.replace('.pdf', '.txt')

df_all = editais_especificos_2023.merge(
    df_all, how='left', on='arquivo'    
)
df_all.sort_values(by='arquivo', inplace=True, ignore_index=True)
df_all['grupo'] = [i // 5 for i in df_all.index]


# ================================================================================
# construindo o prompt e convocando gemini

MODEL_NAME = "gemini-2.0-flash-001"
client = genai.Client(api_key="AIzaSyBwsQ0AGOKVcmxSekEcNoBNRc1zfjH2Zo0")

def ask_gemini(prompt, max_tentativas=5):
    """
    Send a promtp to API Vertex AI with exponential backoff.

    Parameters
    ----------
    prompt : str
        A string (prompt) to sendo to Vertex AI.
    max_tentativas : int, optional
        Number of trials in the exponential backoff. The default is 5.

    Returns
    -------
    str
        A string with a markdown table.

    """
    tentativa = 0
    while tentativa < max_tentativas:
        # model = GenerativeModel(MODEL_NAME)
        try:
           # resposta = model.generate_content(prompt)
           resposta= client.models.generate_content(
               model=MODEL_NAME,
               contents=prompt
           )
           return resposta.text
        except:
            tentativa += 1
            tempo_espera = (2 ** tentativa) + random.random()
            print(f"Limite de taxa atingido. Esperando {tempo_espera:.2f} segundos...")
            time.sleep(tempo_espera)

    print("Número máximo de tentativas excedido.")
    return None

def make_prompt(editais, pergunta):
    """
    Generate a prompt using texts and a question.

    Parameters
    ----------
    editais : pd.Series
        list of texts.
    pergunta : str
        a question to be answered.

    Returns
    -------
    str
        string to be send to API gemini.

    """
    texto = f"""Você é um analista de dados especializado em análise de editais. Sua principal prioridade é extrair informações precisas e literais dos editais fornecidos, sem inferências ou extrapolações. Caso uma informação solicitada não esteja presente no edital, indique 'Não encontrado' na coluna 'Resposta' e explique brevemente o motivo na coluna 'Linha(s) de Referência'.

Sua tarefa é analisar os seguintes editais (documentos de texto) e responder à seguinte pergunta.

A resposta deve ser formatada em uma tabela markdown completa e formatada de forma consistente, sem quebras de linha indesejadas ou caracteres extras. Certifique-se de que cada célula contenha apenas o texto relevante.

A tabela markdown deve conter as seguintes colunas:

* Nome do arquivo: O nome que o arquivo estava salvo no computador. Exemplo: 18_editais_especificos_17.txt.
* Nome do Edital: O nome do edital. Exemplo: EDITAL Nº 01/2023.
* Ente Federativo: Indique o nome do ente federativo (o nome do estado ou o nome do município). Se não for possível determinar, coloque "Não identificado". Exemplo: Goiás.
* Ano: ano que o edital fui publicado com quatro dígitos. Exemplo: 2023.
* Resposta: Uma resposta concisa e clara para a pergunta. Se for necessário listar mais de uma opção como resposta, separe os valores por ponto e vírgula. Exemplo: Pessoa Física (a própria pessoa a ser contemplada); Pessoa Física (representando outra a ser a ser contemplada); Pessoa jurídica com fins lucrativos (Sociedade empresária, Sociedade simples); Pessoa jurídica sem fins lucrativos (Organização da sociedade civil). Outro exemplo: 1700000,00.
* Linha(s) de Referência: A(s) linha(s) do edital que você usou para responder à pergunta. Caso não seja possível incluir essa(s) linha(s), explique brevemente o motivo. Na coluna 'Linha(s) de Referência', liste todas as linhas ou seções do edital que foram usadas para formular a resposta. Se a resposta for baseada em múltiplas partes do edital, inclua todas elas.

Certifique-se de que a resposta seja precisa e extraída diretamente e exclusivamente dos editais fornecidos.

Cada linha da tabela markdown corresponde a um único arquivo, e cada arquivo corresponde a uma única linha da tabela markdown. Exemplo, o arquivo 2_editais_especificos_2.txt tem uma, e uma única linha, na tabela markdown.

Cada arquivo precisa ter uma única linha na tabela markdown.

Não inclua tabelas na coluna "Linha(s) de Referência:".

Não inclua o caracter "\n" nas células da tabela markdown.

É obrigatório que a tabela markdown tenha seis colunas: "Nome do arquivo", "Nome do edital", "Ente Federativo", "Ano", "Resposta", "Linha(s) de Referência".

As linhas da tabela precisam corresponder a estes arquivos: {", ".join(editais.arquivo)}. Ou seja, os valores da coluna "Nome do arquivo" são {", ".join(editais.arquivo)}.

Não invente informações. Se um edital não contém a informação necessária para responder à pergunta, indique isso na coluna 'Resposta' e explique brevemente na coluna 'Linha(s) de Referência'.

Abaixo incluo o texto de {editais.shape[0]} editais (arquivos). Garanta que a tabela markdown tenha {editais.shape[0]} linhas: uma linha para cada edital (arquivo). 
 
"""
    for i in editais.index:
        texto += "\n---\n\n"
        texto += f"# Arquivo:\nO edital estava salvo como {editais.loc[i, 'arquivo']}.\n\nEdital publicado por: {editais.loc[i, 'nome_ente']}.\n\n"
        texto += f"# Conteúdo:\n{editais.loc[i, 'texto']}\n\n"
    texto += "\n---\n\n"
    texto += f"# Pergunta:\n{pergunta}\n\n"
    texto += "# Resposta em tabela Markdown:\n"
    return texto



for iter in range(len(variaveis)):
    variavel = variaveis[iter]
    
    output_dir = 'dados/processados/vertex_ai_editais_proprios/' +      variavel.strip('.txt') + '/'
    
    with open('documentos/prompts/' + variavel) as f:
       questao = f.read()
    
    for grupo in sorted(list(set(df_all['grupo']))):
        print(f'{grupo =} | {variavel =} | {iter=}')
        editais = df_all.loc[df_all['grupo'] == grupo, :]
        
        prompt = make_prompt(editais, questao)
        
        time.sleep(2)
        
        resposta = ask_gemini(prompt, max_tentativas=10)
        if not None:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(f'{output_dir}/grupo_{grupo}_{variavel.strip(".txt")}.txt', 'w') as file:
                file.write(resposta)


for iter in range(len(variaveis)):    
    # colocando so resultados em planilha de excel
        
    variavel = variaveis[iter]
    output_dir = 'dados/processados/vertex_ai_editais_proprios/' + variavel.strip('.txt') + '/'
    arq_md = os.listdir(output_dir)
    nome_arquivo = []
    nome_edital = []
    estado = []
    ano = []
    answer = []
    justificativa = []
    
    for arq in arq_md:
        # print(f'{arq = }')
        f = open(output_dir + arq)
        nome_arquivo_aux = []
        nome_edital_aux = []
        estado_aux = []
        ano_aux = []
        answer_aux = []
        justificativa_aux = []
        for line in f.readlines():
            # print(f"{line=}")
            if not line.startswith('```markdown') and not re.match(r'\|.+---.+\|.+', line) and not line.startswith('```') and line.startswith("|"):
                regex = re.search(r"^\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|.*", line, re.IGNORECASE)
                # print(f'{len(regex.groups())}')
                nome_arquivo_aux.append(regex.group(1).strip())
                nome_edital_aux.append(regex.group(2).strip())
                estado_aux.append(regex.group(3).strip())
                ano_aux.append(regex.group(4).strip())
                answer_aux.append(regex.group(5).strip())
                justificativa_aux.append(regex.group(6).strip())
        f.close()
         
        nome_arquivo_aux.pop(0)
        nome_edital_aux.pop(0)
        estado_aux.pop(0)
        ano_aux.pop(0)
        answer_aux.pop(0)
        justificativa_aux.pop(0)
        print(f'{len(nome_arquivo_aux)=} | {arq=}')
        
        nome_arquivo.extend(nome_arquivo_aux)
        nome_edital.extend(nome_edital_aux)
        estado.extend(estado_aux)
        ano.extend(ano_aux)
        answer.extend(answer_aux)
        justificativa.extend(justificativa_aux)
    
    df_final = pd.DataFrame({
        'nome_arquivo': nome_arquivo,
        'nome_edital': nome_edital,
        'estado': estado,
        'ano': ano,
        'answer': answer,
        'justificativa': justificativa
    })
    df_final.to_excel(f'dados/processados/vertex_ai_editais_proprios/{variavel.strip(".txt")}.xlsx', index=False)
