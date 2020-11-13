import psycopg2
from werkzeug.security import generate_password_hash
import psycopg2.extras

def create():
  connection = psycopg2.connect(user = "postgres",
                                  password = "sid562554",
                                  host = "localhost",
                                  port = "5432",
                                  database = "Exercise")


  with connection:
    with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
      curs.execute('''CREATE TABLE IF NOT EXISTS sign(
                    email varchar,
                    name varchar,
                    password varchar)''')
    curs.close()

  connection.close()

def create_1():
  connection = psycopg2.connect(user = "postgres",
                                  password = "sid562554",
                                  host = "localhost",
                                  port = "5432",
                                  database = "Exercise")


  with connection:
    with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
      curs.execute('''CREATE TABLE IF NOT EXISTS info(
                    email varchar,
                    name varchar,
                    age int,
                    sex varchar,
                    blood_group varchar,
                    ph BIGint,
                    address varchar,
                    image_path varchar)''')
      curs.close()

  connection.close()


if __name__ =="__main__":
    create_1()