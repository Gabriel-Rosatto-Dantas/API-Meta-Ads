"""
Arquivo de configuração para o projeto Meta Ads API.
"""

# Configurações da API do Facebook
FB_API_VERSION = "v20.0"
FB_BASE_URL = f"https://graph.facebook.com/{FB_API_VERSION}"

# Campos padrão para consultas à API
DEFAULT_API_FIELDS = [
    "spend",
    "cpc",
    "cpm",
    "objective",
    "adset_name",
    "adset_id",
    "clicks",
    "campaign_name",
    "campaign_id",
    "conversions",
    "frequency",
    "conversion_values",
    "ad_name",
    "ad_id"
]

# Configurações de retry para requisições à API
API_RETRY_CONFIG = {
    "total": 3,
    "backoff_factor": 1,
    "status_forcelist": [500, 502, 503, 504]
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "handlers": [
        "FileHandler",
        "StreamHandler"
    ],
    "log_file": "meta_ads.log"
}

# Configurações do BigQuery
BIGQUERY_CONFIG = {
    "if_exists": "replace",
    "chunksize": 10000
} 