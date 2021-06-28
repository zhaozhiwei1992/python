import os

# from configuration.Configuration import Configuration

"""
这个文件中总共分为4各类，Config父类里面是基础配置，下面的3个子类继承基础配置并根据自己的需求修改配置信息其中ProductionConfig、TestingConfig、DevelopmentConfig分别代表生产环境、测试环境、开发环境。
"""


class Config(object):
    """默认配置"""
    DEBUG = False
    TESTING = False
    # CON = Configuration()
    # HOSTS = CON.HOSTS
    # URL = CON.URL
    # MAC = CON.MAC


class ProductionConfig(Config):
    """生产环境"""
    ENV = 'production'
    DATABASE_URI = ''
    SECRET_KEY = ''


class DevelopmentConfig(Config):
    """开发环境"""
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE = db_path = os.getcwd() + '/db.sqlite3'
    SECRET_KEY = 'dev'


class TestingConfig(Config):
    """测试环境"""
    TESTING = True
