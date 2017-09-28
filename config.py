import os



class Config(object):
    """Classe usata per la configurazione dell'oggetto app di classe Flask"""
    SECRET_KEY= os.environ['SECRET_KEY']

class ProductionConfig(Config):
   DEBUG=True
   SERVER_NAME = 'localhost:8000'
   MAX_CONTENT_PATH=16*1024*1024
   MAIL_SERVER =os.environ['MAIL_SERVER']
   MAIL_PORT = 587
   MAIL_USE_TLS = True
   MAIL_USE_SSL = False
   MAIL_USERNAME = os.environ['MAIL_USERNAME']
   MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
   ISBN_TOKEN = os.environ['ISBN_TOKEN']
   GOOGLE_TOKEN = os.environ['GOOGLE_TOKEN']


class DevelopmentConfig(Config):
   pass

myconfig=ProductionConfig()
