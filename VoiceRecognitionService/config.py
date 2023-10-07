import logging

class DefaultConfig:
    DEBUG = False
    # default configs here

class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

class TestingConfig(DefaultConfig):
    LOG_LEVEL = logging.INFO

class ProductionConfig(DefaultConfig):
    LOG_LEVEL = logging.WARNING
