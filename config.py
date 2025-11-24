class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Iforgot2%23@localhost/mechanic_db'
    DEBUG = True


class TestingConfig:
    pass

class ProductionConfig:
    pass

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'