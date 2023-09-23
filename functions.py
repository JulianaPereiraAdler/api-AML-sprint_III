from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import pandas as pd
import re
import smtplib
import json
import string
import os
import requests
import zipfile
import io
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import base64


def send_mail(to_address, titulo, html):
    from_address = 'portalcadastro.emailteste@gmail.com'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = titulo
    msg['From'] = from_address
    # if isinstance(to_address,list):
    #     msg['To'] = ", ".join(to_address)
    # else:
    #     msg['To'] = to_address
    part1 = MIMEText(html, 'html')
    msg.attach(part1)
    username = 'portalcadastro.emailteste@gmail.com'
    password = 'ambepemmmknvrrzd'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_address, to_address, msg.as_string())
    server.quit()


def send_mail_local(to_address, titulo, html):
   # conexão com os servidores do google
    smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_port = 465
    # username ou email para logar no servidor
    username = 'portalcadastro.emailteste@gmail.com'
    password = 'ambepemmmknvrrzd'

    from_addr = 'portalcadastro.emailteste@gmail.com'

    # a biblioteca email possuí vários templates
    # para diferentes formatos de mensagem
    # neste caso usaremos MIMEText para enviar
    # somente texto
    message = MIMEText(html, 'html')
    message['subject'] = titulo
    message['from'] = from_addr
    message['to'] = to_address

    # conectaremos de forma segura usando SSL
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    # para interagir com um servidor externo precisaremos
    # fazer login nele
    server.login(username, password)
    server.sendmail(from_addr, to_address, message.as_string())
    server.quit()
        
    return "true"


def decrypt(encrypted_data_str, password):
    # Desserializar os dados criptografados
    encrypted_data = json.loads(base64.b64decode(encrypted_data_str).decode())
    
    salt = base64.b64decode(encrypted_data['salt'])
    iv = base64.b64decode(encrypted_data['iv'])
    ct = base64.b64decode(encrypted_data['ciphertext'])
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return (decryptor.update(ct) + decryptor.finalize()).decode()


def diligencia_compliance_inicial(cpf, nome, API_Key):
    #realiza diligencia de compliance inicial e retorna html para ser enviado por email para o complinace

    html_resposta_header = '<p style="padding-bottom:10px;"><b>Castrodro do Investidor '+ nome.upper() +'('+cpf+') foi concluído. </b></p>'
    html_resposta_header = html_resposta_header + '<p style="padding-bottom:10px;"><b><u>Diligência de Compliance Inicial</u></b></p>'

    first_name = nome.split()[0]
    last_name = nome.split()[-1]
    full_name = first_name + " " + last_name

    ## Scrapping Portal da Transparencia 
    html_resposta = '<p><u>Consulta PEP pelo Portal da Transparência (gov.br):</u></p>'

    middle_numbers = cpf[4:10]

    url = "https://portaldatransparencia.gov.br/download-de-dados/pep"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        script_tags = soup.find_all('script', text=re.compile('arquivos.push'))

        mes_arquivo = None
        for script in script_tags:
            match = re.search(r'"mes"\s*:\s*"(\d+)"', script.string)
            if match:
                mes_arquivo = match.group(1)
                break

        ano_arquivo = None
        for script in script_tags:
            match = re.search(r'"ano"\s*:\s*"(\d+)"', script.string)
            if match:
                ano_arquivo = match.group(1)
                break

        url = "https://portaldatransparencia.gov.br/download-de-dados/pep/"+ str(ano_arquivo) + str(mes_arquivo)
        response_arquivo = requests.get(url, headers=headers)

        if response_arquivo.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response_arquivo.content)) as zf:
                zip_info = zf.infolist()[0]
                data = pd.read_csv(zf.open(zip_info.filename), sep=";", encoding='latin-1')

                matching_rows = data[data['CPF'].str.contains(middle_numbers, na=False)]
                name_matching_rows = matching_rows[
                    (matching_rows['Nome_PEP'].str.contains(first_name, case=False) & matching_rows['Nome_PEP'].str.contains(last_name, case=False)) |
                    (matching_rows['Nome_PEP'].str.contains(last_name, case=False) & matching_rows['Nome_PEP'].str.contains(first_name, case=False))
                ]

            if name_matching_rows.shape[0] == 0:
                html_resposta = html_resposta+ "<p style='color:#326b1f; padding-bottom:10px;'><b>Não é PEP.</b></p><hr>"
            else:
                html_resposta = html_resposta+"<p style='color:#842525; padding-bottom:10px;'><b>É classificado como PEP.</b></p>"

                for index, row in name_matching_rows.iterrows():
                    html_resposta = html_resposta + "<p>Descrição_Função: "+str(row['Descrição_Função'])+ "</p> "
                    html_resposta = html_resposta + "<p>Nível_Função: "+str(row['Nível_Função'])+ "</p> "
                    html_resposta = html_resposta + "<p>Nome_Órgão: "+str(row['Nome_Órgão'])+ "</p> "
                    html_resposta = html_resposta + "<p>Data_Início_Exercício: "+str(row['Data_Início_Exercício'])+ "</p> "
                    html_resposta = html_resposta + "<p>Data_Fim_Exercício: "+str(row['Data_Fim_Exercício'])+ "</p> "
                    html_resposta = html_resposta + "<p style='padding-bottom:10px;'>Data_Fim_Carência: "+str(row['Data_Fim_Carência'])+ "</p><hr> "

        else:
            html_resposta = html_resposta + f"<p style='padding-bottom:10px;'>Erro no Scrapping do Portal da Transparência (gov.br): {response.status_code} </p><hr>"

    else:
        html_resposta = html_resposta + f"<p style='padding-bottom:10px;'>Erro no Scrapping do Portal da Transparência (gov.br): {response.status_code} </p><hr>"

    ## API AML 

    ### Listas Restritivas Internacionais - Web Service para consulta pontual
    url = "https://amlduediligence.com.br/drive/get_lri.php?usuario="+decrypt(API_Key, "0IMPOIfsdf3kopfFDF1MIF#If")+"&pessoa="+full_name
    response_lista_restritiva = requests.get(url)
    html_resposta_aml = "<p style='padding-bottom:10px;'><u>AML Due Diligence</u></p><p><b>Consulta Listas Restritivas Internacionais:</b></p>"

    root = ET.fromstring(response_lista_restritiva.text)
    qtd_value = root.find("qtd").text

    if int(qtd_value) == 0: 
        html_resposta_aml = html_resposta_aml + "<p style='color:#326b1f; padding-bottom:10px;'><b>"+full_name.upper() +" não consta em Listas Restritivas Internacionais.</b>"

    if int(qtd_value) > 0:    
        for cadastro in root.findall('cadastros/cadastro'):
            nome = cadastro.find('nome').text
            origem = cadastro.find('origem').text
            data_nascimento = cadastro.find('datas_nascimento/data_nascimento').text
            documento = cadastro.find('documentos/documento').text
            local_nascimento = cadastro.find('locais_nascimento/local_nascimento').text
            acusacao = cadastro.find('acusacoes/acusacao').text
            procurado = cadastro.find('procurado_por/procurado').text
            data_entrada = cadastro.find('data_entrada').text
            
            html_resposta_aml = html_resposta_aml + "<p style='color:#842525; padding-bottom:10px;'><b>Foram encontradas " + str(qtd_value) + " pessoas para a busca por ''" + full_name + "'.<p></b>" 
            html_resposta_aml = html_resposta_aml + f"<p>Nome: {nome}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Origem:  {origem}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Data Nascimento: {data_nascimento}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Local Nascimento: {local_nascimento}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Acusação: {acusacao}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Procurado: {procurado}</p>"
            html_resposta_aml = html_resposta_aml + f"<p style='padding-bottom:10px;'>Data Entrada: {data_entrada}</p>"
            
    html_resposta_aml = html_resposta_aml + "<hr>"

    ### Listas Restritivas Nacionais - Web Service para consulta pontual
    url = "https://amlduediligence.com.br/drive/get_mm.php?usuario="+decrypt(API_Key, "0IMPOIfsdf3kopfFDF1MIF#If")+"&pessoa="+full_name+"&cpf_cnpj="+cpf
    response_listas_nacionais = requests.get(url)
    html_resposta_aml = html_resposta_aml+'<p><b>Consulta Mídias Tratadas e Listas de Sanções Nacionais:</b></p>'

    root = ET.fromstring(response_listas_nacionais.text)
    qtd_value = root.find("qtd").text

    if int(qtd_value) == 0: 
        html_resposta_aml = html_resposta_aml + "<p style='color:#326b1f; padding-bottom:10px;'><b>"+full_name.upper() +" não consta em Mídias Tratadas e Listas de Sanções Nacionais.</b>"

    if int(qtd_value) > 0:   
        for cadastro in root.findall('cadastros/cadastro'):
            nome = cadastro.get('nome')
            cpf_cnpj_01 = cadastro.get('cpf_cnpj_01')
            conhecido_como = cadastro.get('conhecido_como')
            data = cadastro.get('data')
            envolvimento =  cadastro.get('envolvimento')
            crimes  =  cadastro.get('crimes')
            score =  cadastro.get('score')
            citado_midia = cadastro.get('citado_midia')
            pep = cadastro.get('pep')
            
            html_resposta_aml = html_resposta_aml + "<p style='color:#842525; padding-bottom:10px;'><b>Foram encontradas " + str(qtd_value) + " pessoas para a busca por ''" + full_name + "'.<p></b>" 
            html_resposta_aml = html_resposta_aml + f"<p>Nome: {nome}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>CPF/CNPJ:  {cpf_cnpj_01}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Conhecido Como: {conhecido_como}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Envolvimento: {envolvimento}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Crimes: {crimes}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Data: {data}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Citado Mídia: {citado_midia}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>PEP: {pep}</p>"
            html_resposta_aml = html_resposta_aml + f"<p style='padding-bottom:10px;'>Score: {score}</p>"
            
    html_resposta_aml = html_resposta_aml + "<hr>"

    ### PEP - Web Service para consulta pontual
    url_oep = "https://www.listapep.amlconsulting.com.br/drive/get_pep.php?usuario="+decrypt(API_Key, "0IMPOIfsdf3kopfFDF1MIF#If")+"&cpf_cnpj="+cpf
    response_pep = requests.get(url_oep)

    html_resposta_aml = html_resposta_aml+'<p><b>Consulta PEP (AML Due Diligence):</b></p>'
    root = ET.fromstring(response_pep.text)
    qtd_value = root.find("qtd").text

    if int(qtd_value) == 0: 
        html_resposta_aml = html_resposta_aml + "<p style='color:#326b1f'>"+full_name.upper() +" não consta como PEP."

    if int(qtd_value) > 0:   
        for cadastro in root.findall('cadastros/cadastro'):
            nome = cadastro.get('nome')
            cpf_cnpj = cadastro.get('cpf_cnpj')
            classificacao = cadastro.get('classificacao')
            descricao = cadastro.get('descricao')
            data_inicio = cadastro.get('data_inicio')
            data_fim = cadastro.get('data_fim')
            data_nascimento_fundacao = cadastro.get('data_nascimento_fundacao')
            cidade_uf_cargo = cadastro.get('cidade_uf_cargo')
            data_obito = cadastro.get('data_obito')
            atualizado_em = cadastro.get('atualizado_em')
            oficial_flg = cadastro.get('oficial_flg')
            info_adicional = cadastro.get('info_adicional')
            score = cadastro.get('score')

            html_resposta_aml = html_resposta_aml + "<p style='color:#842525; padding-bottom:10px;'><b>Foram encontradas " + str(qtd_value) + " pessoas para a busca por ''" + full_name + "'.<p></b>" 
            html_resposta_aml = html_resposta_aml + f"<p>Nome: {nome}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>CPF/CNPJ:  {cpf_cnpj}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Classificação: {classificacao}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Descrição: {descricao}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Data Inicio: {data_inicio}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Data Fim: {data_fim}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Data_obito: {data_obito}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Cidade UF Cargo: {cidade_uf_cargo}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Oficial Flag: {oficial_flg}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Informação Adicional: {info_adicional}</p>"
            html_resposta_aml = html_resposta_aml + f"<p>Oficial Flag: {info_adicional}</p>"
            html_resposta_aml = html_resposta_aml + f"<p style='padding-bottom:10px;'>Score: {score}</p>"
            
    html_resposta_aml = html_resposta_aml + "<hr>"

    return html_resposta_header+html_resposta+html_resposta_aml




