# Meta Ads Pipeline de dados para BigQuery
Este projeto automatiza a extração de dados de campanhas publicitárias do Facebook Ads e o carregamento desses dados para o Google BigQuery.

#### 📌 Funcionalidades Principais
Extração de dados da API do Facebook Graph:
Contas de anúncios
Campanhas publicitárias
Conjuntos de anúncios (adsets)
Métricas de desempenho (insights)
Processamento e transformação dos dados
Validação de qualidade dos dados
Carregamento automático para o Google BigQuery
Sistema de fallback para armazenamento local em CSV
Mecanismo de retry para requisições à API
Logging detalhado das operações

#### ⚙️ Pré-requisitos
Python 3.7 ou superior
Conta no Facebook Developers com acesso à API de Marketing
Projeto no Google Cloud Platform com BigQuery ativado
Token de acesso válido para a API do Facebook
Credenciais de serviço do Google Cloud

#### 🛠️ Configuração
Clone este repositório:

```bash
git clone [https://github.com/seu-usuario/facebook-ads-bigquery.git](https://github.com/Gabriel-Rosatto-Dantas/API-Meta-Ads/tree/main)
```
Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
Instale as dependências:

```bash
pip install -r requirements.txt
```
Crie um arquivo .env na raiz do projeto com:

```bash
FB_TOKEN=seu_token_do_facebook
GOOGLE_CLOUD_PROJECT_ID=seu-project-id
BIGQUERY_DATASET_ID=seu-dataset-id
GOOGLE_APPLICATION_CREDENTIALS=caminho/para/seu/credentials.json
```
Configure o arquivo config.py com seus parâmetros.\


#### 🚀 Como Executar
Execute o script principal:

```bash
python APP.py
```
#### 📊 Estrutura dos Dados
Campanhas
ID, nome, status, objetivo
Datas de início e término
Status efetivo
Relação com a conta de anúncio
Conjuntos de Anúncios (Adsets)
ID, nome, status
Orçamento diário e total
ID da campanha relacionada
Datas de início e término
Métricas de Desempenho (Insights)
Impressões, cliques, CTR
Gasto, frequência
Resultados e custo por resultado
Período de data

#### 🔧 Configurações Personalizáveis
Edite config.py para ajustar:
DEFAULT_API_FIELDS: Campos padrão dos insights
API_RETRY_CONFIG: Configurações de retry
LOGGING_CONFIG: Configurações de logging
BIGQUERY_CONFIG: Parâmetros do BigQuery

#### 📂 Estrutura do Projeto
```bash
API-Meta-Ads/
├── app.py                # Script principal
├── config.py              # Configurações do projeto
├── .env                   # Variáveis de ambiente
├── requirements.txt       # Dependências do projeto
├── README.md              # Este arquivo
└── logs/                  # Diretório de logs (criado automaticamente)
```
