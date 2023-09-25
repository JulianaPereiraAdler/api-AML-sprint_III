# API de Diligência de Compliance


Este projeto faz parte do MPV da Sprint 3 da Pós Graduação em Engenharia de Software da Juliana Pereira 

### Descrição
A API foi projetada para realizar diligência de compliance em investidores, tanto titulares quanto cotitulares, como parte do processo de cadastro. Foi elaborada em consonância com o disposto na Resolução CVM nº 30/21 e Resolução CVM nº 50/21, visando mitigar o risco de uso inadvertido das Gestora de Investimento como intermediária em processos que buscam ocultar a verdadeira origem de recursos provenientes de atividades criminosas de lavagem de dinheiro e financiamento ao terrorismo.

A API foi implementada seguindo o estilo REST usando Flask.
 - [Flask](https://flask.palletsprojects.com/en/2.3.x/) 

#### Funcionalidades:
- **Verificação de PEP (Pessoa Politicamente Exposta)**: A API realiza um scrapping no portal da transparência do GOV.BR, que contém um cadastro de agentes públicos que desempenharam funções públicas relevantes nos últimos cinco anos. Ela verifica se o nome e CPF do investidor se enquadram como PEP, conforme a Resolução CVM nº 50/21.
  
- **Consulta à API do AML Due Diligence**: A API consulta a API externa do AML Due Diligence para uma avaliação completa de risco reputacional. As listas verificadas incluem:
  - **Mídias Tratadas e Listas de Sanções Nacionais**: Esta lista contém informações de indivíduos e empresas identificados na mídia ou em listas restritivas devido ao envolvimento em crimes antecedentes à lavagem de dinheiro.
  - **Listas Restritivas Internacionais**: Engloba o monitoramento de listas que auxiliam na mitigação do risco de imagem e envolvimento em atividades internacionais ligadas ao financiamento ao terrorismo.
  - **Lista PEP Nacional**: Contém mais de 1 milhão de perfis de CPF e CNPJ de pessoas politicamente expostas e relacionadas, monitoradas e atualizadas em tempo real a partir de listas oficiais.
  
- **Notificação por Email**: Após a diligência, um email é disparado ao responsável contendo o resultado da verificação.

A documentação completa da API externa pode ser encontrada em [AML Due Diligence](https://www.amlreputacional.com.br/aml-due-diligence/).

---
### Instalação

Certifique-se de ter todas as bibliotecas Python listadas no `requirements.txt` instaladas. Após clonar o repositório, navegue ao diretório raiz pelo terminal para executar os comandos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).
> No Ambiente Windows foi utilizado o comando (python -m venv env) para a criação do ambiente virtual e o comando (env\Scripts\activate) para ativar o ambiente virtual.

```
(env)$ pip install -r requirements.txt
```
Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

---
### Executando o servidor

Para iniciar a API, execute:

```
(env)$ flask run --host 0.0.0.0 --port 5001
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor automaticamente após uma mudança no código fonte. 

```
(env)$ flask run --host 0.0.0.0 --port 5001 --reload
```

---
### Acesso no browser

Abra o [http://localhost:5001/#/](http://localhost:5001/#/) no navegador para verificar o status da API em execução.

---
## Como executar através do Docker

Certifique-se de ter o [Docker](https://docs.docker.com/engine/install/) instalado e em execução em sua máquina.

Navegue até o diretório que contém o Dockerfile e o requirements.txt no terminal.
Execute **como administrador** o seguinte comando para construir a imagem Docker:

```
$ docker build -t rest-api_aml .
```

Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run -p 5001:5001 rest-api_aml
```

Uma vez executando, para acessar a API, basta abrir o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador.



### Alguns comandos úteis do Docker

>**Para verificar se a imagem foi criada** você pode executar o seguinte comando:
>
>```
>$ docker images
>```
>
> Caso queira **remover uma imagem**, basta executar o comando:
>```
>$ docker rmi <IMAGE ID>
>```
>Subistituindo o `IMAGE ID` pelo código da imagem
>
>**Para verificar se o container está em exceução** você pode executar o seguinte comando:
>
>```
>$ docker container ls --all
>```
>
> Caso queira **parar um conatiner**, basta executar o comando:
>```
>$ docker stop <CONTAINER ID>
>```
>Subistituindo o `CONTAINER ID` pelo ID do conatiner
>
>
> Caso queira **destruir um conatiner**, basta executar o comando:
>```
>$ docker rm <CONTAINER ID>
>```
>Para mais comandos, veja a [documentação do docker](https://docs.docker.com/engine/reference/run/).
