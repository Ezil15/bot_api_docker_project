from config import *
from mysql.connector import connect, cursor


db = connect(
  host=SQL_HOST,
  user=SQL_USER,
  password=SQL_PASSWORD,
  database = SQL_DATABASE
)

cursor =  db.cursor()
