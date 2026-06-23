import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-qing-zai-zheng-shi-huan-jing-bian-geng')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///C:/Users/user/Documents/motorcycle_data/data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    APP_NAME = '漢堡車隊報名系統'
    APP_LANG = 'zh-Hant'
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {'development': DevelopmentConfig, 'production': ProductionConfig, 'default': DevelopmentConfig}


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

