# Werkzeug
## Simple Web App For Finding Blood Doner

Follow following steps to make sure the app runs:

1. It is recommended to create the new environment for each project:(So, create and activate your environment)
> virtualenv newenv

> source newenv/bin/activate

2. Do install all the requirements.
 > pip install -m requirements.txt

3. Make sure you check the Database section on db.py and also on project.py. And add the configuration for the system:
``` 
#On project.py make sure you change the configuration variable(on line 214)
configuration = {
    'POSTGRES_DATABASE_NAME': 'database_name',
    'POSTGRES_DATABASE_USER': 'database_user',
    'POSTGRES_DATABASE_PASSWORD': 'user_password',
    'POSTGRES_HOST': 'localhost'
}
```
```
#On db.py while connecting psycopg2 make sure credentials are from your own database
def create():
  connection = psycopg2.connect(user = "database_user",
                                  password = "user_password",
                                  host = "localhost",
                                  port = "5432",
                                  database = "database_name")



```

4. Then first run db.py to create all the necessary tables on the database:
> python db.py

5. Then finally run the server.
> python project.py

