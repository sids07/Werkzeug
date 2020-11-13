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
from werkzeug.local import Local

from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2 import sql
import psycopg2.extras

# Request data takes the environ object and allow to acess data from environ in proper manner
# Response object is WSGI application in itself and provides a much nicer way to create response

# Application class is a WSGI application
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
        static = os.path.join(os.path.dirname(__file__), 'static')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                 autoescape=True)
        self.url_map = Map([
                            Rule('/',endpoint='home'),
                            Rule('/login', endpoint='login'),
                            Rule('/shorty',endpoint='main'),
                            Rule('/update',endpoint='update_form'),
                            Rule('/update_change',endpoint='update'),
                            Rule('/delete',endpoint='delete'),
                            Rule('/signup',endpoint='signup'),
                            Rule('/create',endpoint='create'),
                            Rule('/doner',endpoint='donate'),
                            Rule('/profile',endpoint='profile'),
                            Rule('/upload',endpoint='upload'),
                            Rule('/donation_form',endpoint='donation_form'),
                            Rule('/profile_create',endpoint='profile_create')

])
        self.validate= False
        
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

    def on_home(self,request):
               
        return self.render_template('home.html',validate=self.validate)

    def on_donation_form(self,request):
        return self.render_template('donation_form.html',validate=self.validate)
    def on_upload(self,request):
        files = request.files["uploaded_file"]
        s = f"static/{files.filename}"
        files.save(s,buffer_size=16384)
        files.close()
        '''
        for f in files:
            fh = open(f"static/{f.filename}","wb")
            fh.write(f.body)
            fh.close()
        ''' 
        return self.render_template('home.html',validate=self.validate, a= files.filename)

    def on_profile_create(self,request):
        e = self.old_email
        form_name = request.form.get('name')
        form_age = request.form.get('age')
        form_address= request.form.get('address')
        form_sex = request.form.get('sex')
        form_blood = request.form.get('blood')
        form_ph = request.form.get('ph')
        files = request.files.get("uploaded_file")
        s = f"static/{files.filename}"
        files.save(s,buffer_size=16384)
        files.close()

        cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('''INSERT INTO info (email,name,age,sex,blood_group,ph,address,image_path) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',(e,form_name,form_age,form_sex,form_blood,form_ph,form_address,files.filename))
        self.postgres_conn.commit()
        return self.render_template("home.html",validate=self.validate)
    def on_profile(self,request):
        a = self.old_email
        #print(a)
        cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('''Select * from info WHERE email=%(user)s''',{'user':a});

        data = cursor.fetchone()
        #print(data)
        if data is None:
            return self.render_template('create.html',validate=self.validate)            
        else:
            return self.render_template('profile.html',validate=self.validate,inc=data)
    def on_login(self,request):
        self.validate = False
        return self.render_template('new_url.html',validate=self.validate)

    def on_donate(self,request):
        cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('''Select * from info''')

        info = cursor.fetchall()

        return self.render_template('donate.html',info=info,validate=self.validate)
 
    def on_create(self,request):
        email = request.form.get('email')
        name = request.form.get('name')
        pas = request.form.get("psw")
        password = generate_password_hash(pas)
        confirm = check_password_hash(password,request.form.get("psw-repeat"))

        if confirm == False:
            return self.render_template('signup.html',message="Passwords didn't match")
        else:
            cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute('''INSERT INTO sign (email,name,password) VALUES (%s,%s,%s)''',(email,name,password))
            self.postgres_conn.commit()
            return self.render_template('new_url.html',messsage="Account Created")


    def on_signup(self,request):
        return self.render_template('signup.html')

    def on_update_form(self,request):
        cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('''Select * from info WHERE email=%(user)s''',{'user':self.old_email});

        data = cursor.fetchone()
        return self.render_template('form.html',up=data,validate=self.validate)

    def on_update(self,request):
        a = self.old_email
        name_update = request.form.get('name')
        age_update = request.form.get('age')
        blood_update= request.form.get('blood')
        pic_update= request.files['uploaded_file']
        print(len(pic_update.filename))

        if len(pic_update.filename) == 0:
            cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute('''UPDATE info SET name=%(name)s, age=%(age)s, blood_group=%(blood)s WHERE email=%(old)s''',{'name':name_update,'age':age_update,'blood':blood_update,'old':a})
            self.postgres_conn.commit()
            return self.render_template('home.html',validate=self.validate)
        else:
            s = f"static/{pic_update.filename}"
            pic_update.save(s,buffer_size=16384)
            pic_update.close()

            cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute('''UPDATE info SET name=%(name)s, age=%(age)s, blood_group=%(blood)s, image_path=%(path)s WHERE email=%(old)s''',{'name':name_update,'age':age_update,'blood':blood_update,'path':pic_update.filename,'old':a})
            self.postgres_conn.commit()
            return self.render_template('home.html',validate=self.validate)

    def on_delete(self,request):
        cursor = self.postgres_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('''DELETE FROM info WHERE email=%(email)s
        ''',{'email':self.old_email})
        self.postgres_conn.commit()
        return self.render_template('home.html',message='Deleted ',validate=self.validate)

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
        cursor.execute('''select * from sign where email=%(user)s''',{'user':email1});
        #cursor.execute(query)
        main_data = cursor.fetchone()
        if main_data==None:
            return self.render_template('new_url.html',message="Either password or email provided is invalid")
        else:
            self.old_email = email1
            self.name = main_data['name']
            validate=check_password_hash(main_data['password'],pas)
            self.validate= validate
            if validate == True:
                return self.render_template('home.html',email=email1,name= main_data['name'],validate=self.validate)
            else:
                return self.render_template('new_url.html',message="Either password or email provided is invalid",validate=self.validate)

    def __call__(self,environ,start_response):
        return self.wsgi_app(environ,start_response)

configuration = {
    'POSTGRES_DATABASE_NAME': 'Exercise',
    'POSTGRES_DATABASE_USER': 'postgres',
    'POSTGRES_DATABASE_PASSWORD': 'sid562554',
    'POSTGRES_HOST': 'localhost'
}

def create_app(config_dict,with_static=True):
    app = Application(config_dict)
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static': os.path.join(os.path.dirname(__file__), 'static')
            })

    return app
# It also allows us to use WSGI Middleware that exports static file.
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app(config_dict=configuration)
    #app.validate()
    
    run_simple('localhost', 8008, app, use_debugger=True, use_reloader=True)