import os

class Config:
    # MySQL connection using PyMySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mallik%40123@localhost/healthcare'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
