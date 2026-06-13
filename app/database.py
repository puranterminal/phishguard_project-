import pymysql
import config

def get_connection():
    try:
        return pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
        )
    except Exception as e:
        print("DB failed:", e)