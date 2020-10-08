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
            curs.execute('''CREATE TABLE IF NOT EXISTS details(
                    email varchar,
                    age integer,
                    password varchar)''')
        curs.close()


        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
            curs.execute("INSERT INTO details VALUES (%s, %s, %s);",
             ('sid@gmail.com', 20, generate_password_hash('mango07')))
            curs.execute("INSERT INTO details VALUES (%s, %s, %s);",
             ('sid06@gmail.com', 21, generate_password_hash('mango007')))
            curs.execute("INSERT INTO details VALUES (%s, %s, %s);",
             ('sid07@gmail.com', 22, generate_password_hash('mango0007')))
        curs.close()

    connection.close()

if __name__ =="__main__":
    create()