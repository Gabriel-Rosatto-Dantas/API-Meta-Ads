import requests
import json
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas_gbq
from google.oauth2 import service_account
import tempfile
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
from config import (
    FB_BASE_URL,
    DEFAULT_API_FIELDS,
    API_RETRY_CONFIG,
    LOGGING_CONFIG,
    BIGQUERY_CONFIG
)

# Configuração do logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["log_file"]),
        logging.StreamHandler()
    ]
)

class GraphAPI:
    """
    Classe para interagir com a API do Facebook Graph.
    
    Attributes:
        base_url (str): URL base da API do Facebook Graph
        api_fields (list): Campos a serem retornados pela API
        fb_token (str): Token de acesso do Facebook
    """
    
    def __init__(self, fb_token):
        self.base_url = FB_BASE_URL
        self.api_fields = DEFAULT_API_FIELDS
        self.fb_token = "&access_token=" + fb_token
        
        # Configuração do mecanismo de retry
        self.session = requests.Session()
        retries = Retry(**API_RETRY_CONFIG)
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
    
    def _make_request(self, url):
        """
        Faz uma requisição à API com retry automático.
        
        Args:
            url (str): URL da requisição
            
        Returns:
            dict: Resposta da API em formato JSON
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return json.loads(response.content.decode("utf-8"))
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição à API: {str(e)}")
            return {'error': {'message': str(e)}}
    
    def get_ad_accounts(self):
        """
        Obtém todas as contas de anúncios associadas ao token.
        
        Returns:
            list: Lista de contas de anúncios
        """
        url = self.base_url + "/me/adaccounts"
        url += "?fields=id,name,account_status"
        data = self._make_request(url + self.fb_token)
        
        if 'error' in data:
            logging.error(f"Erro ao buscar contas: {data['error']['message']}")
            return []
        return data.get('data', [])
    
    def get_campaigns(self, ad_acc):
        ad_acc = ad_acc.replace('act_', '')
        url = self.base_url + "/act_" + str(ad_acc)
        url += "/campaigns?fields=id,name,status,objective,start_time,end_time,created_time,effective_status"
        response = requests.get(url + self.fb_token)
        data = json.loads(response.content.decode("utf-8"))
        
        if 'error' in data:
            print(f"Erro ao buscar campanhas: {data['error']['message']}")
            return []
            
        return data.get('data', [])
    
    def get_adsets(self, ad_acc):
        ad_acc = ad_acc.replace('act_', '')
        url = self.base_url + "/act_" + str(ad_acc)
        url += "/adsets?fields=id,name,status,campaign_id,daily_budget,lifetime_budget,start_time,end_time,created_time,effective_status"
        response = requests.get(url + self.fb_token)
        data = json.loads(response.content.decode("utf-8"))
        
        if 'error' in data:
            print(f"Erro ao buscar adsets: {data['error']['message']}")
            return []
            
        return data.get('data', [])
    
    def get_insights(self, ad_acc, level="campaign"):
        ad_acc = ad_acc.replace('act_', '')
        url = self.base_url + "/act_" + str(ad_acc)
        url += "/insights?level=" + level
        url += "&fields=" + ",".join(self.api_fields)
        
        data = requests.get(url + self.fb_token)
        data = json.loads(data._content.decode("utf-8"))
        return data

def validate_dataframe(df, name):
    """
    Valida se um DataFrame está vazio ou contém dados inválidos.
    
    Args:
        df (pandas.DataFrame): DataFrame a ser validado
        name (str): Nome do DataFrame para logging
        
    Returns:
        bool: True se o DataFrame é válido, False caso contrário
    """
    if df.empty:
        logging.warning(f"DataFrame {name} está vazio")
        return False
    
    # Verifica valores nulos
    null_counts = df.isnull().sum()
    if null_counts.any():
        logging.warning(f"DataFrame {name} contém valores nulos:\n{null_counts[null_counts > 0]}")
    
    # Verifica tipos de dados
    logging.info(f"Tipos de dados do DataFrame {name}:\n{df.dtypes}")
    
    return True

def upload_to_bigquery(df, table_id, credentials):
    """
    Faz upload de um DataFrame para o BigQuery.
    
    Args:
        df (pandas.DataFrame): DataFrame a ser carregado
        table_id (str): ID da tabela no BigQuery
        credentials: Credenciais do Google Cloud
    
    Raises:
        Exception: Se houver erro no upload
    """
    # Valida o DataFrame antes do upload
    if not validate_dataframe(df, table_id):
        raise ValueError(f"DataFrame {table_id} não passou na validação")
    
    try:
        pandas_gbq.to_gbq(
            df,
            table_id,
            project_id=credentials.project_id,
            credentials=credentials,
            **BIGQUERY_CONFIG
        )
        logging.info(f"Dados carregados com sucesso para a tabela {table_id}")
    except Exception as e:
        logging.error(f"Erro ao carregar dados para {table_id}: {str(e)}")
        raise

def save_to_csv(df, filename):
    """
    Salva um DataFrame em um arquivo CSV no diretório temporário.
    
    Args:
        df (pandas.DataFrame): DataFrame a ser salvo
        filename (str): Nome do arquivo CSV
    
    Returns:
        str: Caminho completo do arquivo salvo
    """
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    df.to_csv(filepath, index=False)
    logging.info(f"Arquivo salvo em: {filepath}")
    return filepath

def main():
    """
    Função principal que coordena a coleta e upload dos dados.
    """
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Configurações do BigQuery
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    dataset_id = os.getenv('BIGQUERY_DATASET_ID')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Verifica se as variáveis de ambiente estão configuradas
    if not all([project_id, dataset_id, credentials_path]):
        logging.error("Variáveis de ambiente não configuradas corretamente.")
        logging.error("Verifique se GOOGLE_CLOUD_PROJECT_ID, BIGQUERY_DATASET_ID e GOOGLE_APPLICATION_CREDENTIALS estão definidas no arquivo .env")
        return
    
    # Remove caracteres especiais e espaços do project_id e dataset_id
    project_id = project_id.replace('-', '_').replace(' ', '_')
    dataset_id = dataset_id.replace('-', '_').replace(' ', '_')
    
    print(f"Project ID: {project_id}")
    print(f"Dataset ID: {dataset_id}")
    
    # Configura as credenciais
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/bigquery"],
    )
    
    # Inicializa a API do Facebook
    fb_token = os.getenv('FB_TOKEN')
    api = GraphAPI(fb_token)
    
    # Obtém todas as contas de anúncios
    ad_accounts = api.get_ad_accounts()
    
    if not ad_accounts:
        print("Nenhuma conta de anúncios encontrada.")
        return
    
    # Coleta dados de todas as contas
    all_campaigns = []
    all_adsets = []
    all_insights = []
    
    for account in ad_accounts:
        print(f"Coletando dados da conta: {account['name']}")
        
        # Coleta campanhas
        campaigns = api.get_campaigns(account['id'])
        for campaign in campaigns:
            campaign['account_id'] = account['id']
            campaign['account_name'] = account['name']
            all_campaigns.append(campaign)
            
            # Coleta insights das campanhas
            insights = api.get_insights(account['id'], level="campaign")
            if 'data' in insights:
                for insight in insights['data']:
                    insight['account_id'] = account['id']
                    insight['account_name'] = account['name']
                    all_insights.append(insight)
        
        # Coleta adsets
        adsets = api.get_adsets(account['id'])
        for adset in adsets:
            adset['account_id'] = account['id']
            adset['account_name'] = account['name']
            all_adsets.append(adset)
    
    # Converte para DataFrames
    campaigns_df = pd.DataFrame(all_campaigns)
    adsets_df = pd.DataFrame(all_adsets)
    insights_df = pd.DataFrame(all_insights)
    
    # Adiciona timestamp de coleta
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    campaigns_df['collected_at'] = current_time
    adsets_df['collected_at'] = current_time
    insights_df['collected_at'] = current_time
    
    # Converte colunas de data/hora com UTC
    for df in [campaigns_df, adsets_df]:
        for col in ['start_time', 'end_time', 'created_time', 'collected_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], utc=True)
    
    # Converte colunas de data para insights
    for col in ['date_start', 'date_stop']:
        if col in insights_df.columns:
            insights_df[col] = pd.to_datetime(insights_df[col], utc=True).dt.date
    
    # Upload para o BigQuery
    try:
        # Upload das campanhas
        campaigns_table_id = f"{dataset_id}.campaigns"
        print(f"Tentando fazer upload para: {campaigns_table_id}")
        upload_to_bigquery(campaigns_df, campaigns_table_id, credentials)
        
        # Upload dos adsets
        adsets_table_id = f"{dataset_id}.adsets"
        print(f"Tentando fazer upload para: {adsets_table_id}")
        upload_to_bigquery(adsets_df, adsets_table_id, credentials)
        
        # Upload dos insights
        insights_table_id = f"{dataset_id}.insights"
        print(f"Tentando fazer upload para: {insights_table_id}")
        upload_to_bigquery(insights_df, insights_table_id, credentials)
        
        print("\nDados carregados com sucesso para o BigQuery!")
        
    except Exception as e:
        print(f"\nErro ao carregar dados para o BigQuery: {str(e)}")
        print("\nSalvando dados localmente como backup...")
        
        # Salva os arquivos em um diretório temporário
        save_to_csv(campaigns_df, 'campaigns.csv')
        save_to_csv(adsets_df, 'adsets.csv')
        save_to_csv(insights_df, 'insights.csv')
        
        print("Dados salvos localmente em CSV.")
        

if __name__ == "__main__":
    main()