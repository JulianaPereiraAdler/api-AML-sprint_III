from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import date


class DadosAML(BaseModel):
    """Define os parâmetros para consultar realizar a diligência de compliance inicial."""
    CPF: str
    Nome: str
    API_Key:str
    email_envio: str

class RespostaAML(BaseModel):
    """Retorna o HTML com o resultado da diligência de compliance inicial."""
    html_response:str
