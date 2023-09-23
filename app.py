from flask_openapi3 import OpenAPI, Info, Tag
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, abort, make_response, g
from functools import wraps
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from logger import logger
from typing import Optional
from io import BytesIO

import pandas as pd
import xml.etree.ElementTree as ET

from functions import *
from schemas import *

info = Info(title="API de AML (MVP - Sprint 3)", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.secret_key = "FSDt4kntc43qtc$QfdsfdsfsdAECTN$#CcaF$#Ckanf"

CORS(app)

# definindo tags
doc_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
aml_tag = Tag(name="AML", description="Login do usuário")


@app.get('/swagger', tags=[doc_tag])
def swagger():
    """Redireciona para a documentação Swagger."""
    return redirect('/openapi/swagger')


@app.get('/documentacao', tags=[doc_tag])
def documentacao():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/diligencia_compliance', tags=[aml_tag], responses={"200": RespostaAML, "404": ErrorSchema})
def send_confirmation_code(form: DadosAML):
    """
    Realiza uma diligência de compliance inicial para o cadastro do cotista.
    Passos:
    1. Consulta o CPF do titular e do cotitular (se houver) no Portal da Transparência do gov.br para verificar se algum dos CPFs é classificado como PEP (Pessoa Exposta Politicamente).
    2. Acessa as APIs do sistema de diligência da AML Due Diligence para checar se os investidores constam em Listas Restritivas nacionais e internacionais ou foram citados em algum meio de comunicação.
    3. Envia um e-mail para a gestora informando que o cadastro do cotista foi concluído, juntamente com o resultado encontrado na diligência inicial.
    """
    response_html = diligencia_compliance_inicial(form.CPF, form.Nome, form.API_Key)
    send_mail_local(form.email_envio, "Conclusão Cadastro: "+form.Nome, response_html)

    return jsonify(response_html)
    

