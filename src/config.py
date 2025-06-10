import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER = {'title': 'User API', 'uiversion': 3}


class LocalConfig(Config):
    basedir = os.path.abspath(os.path.dirname(__file__))
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')


class DevConfig(Config):
    basedir = os.path.abspath(os.path.dirname(__file__))
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')


class TestConfig(Config):
    basedir = os.path.abspath(os.path.dirname(__file__))
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


config_by_env = {
    "local": LocalConfig,
    "development": DevConfig,
    "testing": TestConfig,
    "production": ProdConfig
}
