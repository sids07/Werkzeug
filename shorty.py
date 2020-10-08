import os
import redis
import urllib.parse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader
from werkzeug.urls import url_parse

from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2 import sql
import psycopg2.extras

# Request data takes the environ object and allow to acess data from environ in proper manner
# Response object is WSGI application in itself and provides a much nicer way to create response


# Shortly class is a WSGI application
class Application(object):

    def __init__(self,config):
        self.postgres_conn = psycopg2.connect(
            database=config.get('POSTGRES_DATABASE_NAME', 'postgres'),
            user=config.get('POSTGRES_DATABASE_USER', 'postgres'),
            password=config.get('POSTGRES_DATABASE_PASSWORD'),
            host=config.get('POSTGRES_HOST', 'localhost'),
            port=config.get('POSTGRES_PORT', 5432)
        )
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                 autoescape=True)
        self.url_map = Map([
                            Rule('/', endpoint='login'),
                            Rule('/shorty',endpoint='main'),
                            Rule('/update',endpoint='update_form'),
                            Rule('/update_change',endpoint='update'),
                            Rule('/delete',endpoint='delete')

])
        
    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except HTTPException as e:
            return e

    def on_login(self,request):
        return self.render_template('new_url.html')

    def on_update_form(self,request):
        return self.render_template('form.html',email= self.old_email, age=self.age)

    def on_update(self,request):
        a = self.old_email
        email2 = request.form.get('email')
        age_update = request.form.get('age')
        b= self.age
        cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('''UPDATE details SET email=%(email)s, age=%(age)s WHERE email=%(old)s
        ''',{'email':email2,'age':age_update,'old':a})
        self.postgres_conn.commit()
        cursor.close()
        self.postgres_conn.close()
        self.old_email = email2
        self.age = age_update
        return self.render_template('new_url.html',message="Updated")

    def on_delete(self,request):
        cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('''DELETE FROM details WHERE email=%(email)s
        ''',{'email':self.old_email})
        self.postgres_conn.commit()
        cursor.close()
        self.postgres_conn.close()
        return self.render_template('new_url.html',message='Deleted ')

    def wsgi_app(self,environ,start_response):
        # environ is a dict that contains all the incoming information
        # start_response is a function that can be used to indicate start of function
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ,start_response)

    def on_main(self,request):
        email1 = request.form.get('eid')
        pas = request.form.get('passed')

        cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        #query = sql.SQL(""" select * from data where email={} """).format(sql.Identifier(email1),)
        cursor.execute("select * from details where email=%(user)s",{'user':email1});
        #cursor.execute(query)
        main_data = cursor.fetchone()

        if main_data==None:
            return self.render_template('new_url.html',message="Email Wrong")
        else:
            print(main_data['password'])
            print(email1)
            
            self.old_email = email1
            self.age = main_data['age']
            print(pas)
            validate=check_password_hash(main_data['password'],pas)

            if validate == True:
                return self.render_template('try.html',email=email1,age= main_data['age'])
            else:
                return self.render_template('new_url.html',message="Wrong Password")

    def __call__(self,environ,start_response):
        return self.wsgi_app(environ,start_response)

configuration = {
    'POSTGRES_DATABASE_NAME': 'Exercise',
    'POSTGRES_DATABASE_USER': 'postgres',
    'POSTGRES_DATABASE_PASSWORD': 'sid562554',
    'POSTGRES_HOST': 'localhost'
}

def create_app(config_dict):
    app = Application(config_dict)
    return app
# It also allows us to use WSGI Middleware that exports static file.
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app(config_dict=configuration)
    #app.validate()
    
    run_simple('localhost', 8008, app, use_debugger=True, use_reloader=True)