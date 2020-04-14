from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect # I will learn after that will use
from flask import url_for  # I will learn after that will use
from flask import flash    # I will learn after that will use
import pymysql.cursors
import os
import json
import pdb

from peewee import *

app = Flask(__name__)

# db = SqliteDatabase('test.db')
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='demo',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect("/register", code=302)
    else:
        return redirect("/product_list", code=302)

@app.route("/product_list")
def product_list():
    # cuser = Person.select()
    signed_in_text = 'Sign In'
    if not session.get('logged_in'):
        signed_in_text = 'Sign In'
    else:
        signed_in_text = session['username']
    with connection.cursor() as cursor:
        sql = "SELECT * FROM `products` LIMIT 25 OFFSET 0";
        cursor.execute(sql)
        records = cursor.fetchall()


    for i, product in enumerate(records):
        # pdb.set_trace()
        records[i]['image_url'] = json.loads(product['images'].replace("\'", "\""))['xlarge']['url']

    return render_template('category.html', result=records, signed_in_text=signed_in_text)


@app.route("/product/<id>",methods=['GET'])
def product(id):
    # cuser = Person.select()
   
    signed_in_text = session['username']
    with connection.cursor() as cursor:
        # pdb.set_trace()
        sql = "SELECT * FROM products WHERE id = %s LIMIT 1" % id
        cursor.execute(sql)
        records = cursor.fetchall()

    for i, product in enumerate(records):
        # pdb.set_trace()
        records[i]['image_url'] = json.loads(product['images'].replace("\'", "\""))['xxlarge']['url']
    with connection.cursor() as cursor:
        sql="SELECT COUNT(*) AS fcount FROM ratings WHERE product_id = %s LIMIT 1" % id
        # print(sql)
        cursor.execute(sql)
        feedback_count= cursor.fetchall()[0]['fcount']
        sql="SELECT AVG(rating) AS favg FROM ratings WHERE product_id = %s LIMIT 1" % id
        # print(sql)
        cursor.execute(sql)
        feedback_average= cursor.fetchall()[0]['favg']

    product = records[0]
    if session.get('logged_in'):
        return render_template('product.html', product=product,signed_in_text=signed_in_text, feedback_count=feedback_count,feedback_average=feedback_average)
    else:
        return render_template('login.html')

@app.route("/product/<id>/rating",methods=['POST'])
def rating(id):
    if request.method == 'POST':
        sql = """
        INSERT INTO ratings (firstname, lastname, username, email, pw, rating, product_id) 
        VALUES ('%s', '%s','%s', '%s','%s',%s, %s);""" % (session.get('firstname'),session.get('lastname'),session.get('username'),session.get('email'),session.get('pw'),request.form['rating'],id)
        # print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()

    return redirect("/product/%s" % id, code=302)



@app.route("/login",methods=['GET'])
def glogin():
    # records = Person.select()

    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect("/", code=302)

@app.route("/login",methods=['POST'])
def login():
    if  request.method == 'POST':
        username = request.form['username']
        pw = request.form['password']
        sql = "SELECT * FROM userlists WHERE username = '%s'" % username
        with connection.cursor() as cursor:
            cursor.execute(sql)
            user = cursor.fetchall()
        
        print("sdfdsafdjlsajfd");
        if user[0]['pw'] == pw:
            session['logged_in'] = True
            session['username'] = username
            session['pw'] = pw
            session['firstname'] = user[0]['firstname']
            session['lastname'] = user[0]['lastname']
            session['email'] = user[0]['email']
            
            return redirect("/", code=302)
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route("/register",methods=['GET'])
def register():
    return render_template('registe.html')

@app.route("/register",methods=['POST'])
def register_post():
    if  request.method == 'POST':

        username = request.form['username']
        pw = request.form['password']
        firstname = request.form['First Name']
        lastname = request.form['Last Name']
        email = request.form['email']
        sql = """
        INSERT INTO userlists (firstname, lastname, username, email, pw ) 
        VALUES ('%s', '%s','%s', '%s','%s');""" % (firstname, lastname, username, email, pw)
        # print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()

        # tempData = Person(username=username,pw=pw,fname=firstname,lname=lastname,email=email,active=True)
        # tempData.save()
        
        # login_user = [tempData]
        session['logged_in'] = True
        session['username'] = username
        session['pw'] = pw
        session['email'] = email
        session['firstname']= firstname
        session['lastname'] = lastname
        return redirect("/", code=302)
#@app.route("/template")
#def template():
#    return render_template('template.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect("/", code=302)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/admin",methods=['GET'])
def admin():
    with connection.cursor() as cursor:
        users1= cursor.execute("SELECT username FROM ratings")
        users2= cursor.execute("SELECT username FROM userlists")

    return render_template('admin_dashboard.html', users1=users1,users2=users2)

@app.route("/admin_users",methods=['GET'])
def admin_users():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM userlists")
        users = cursor.fetchall()

    return render_template('admin_users.html',users=users)

@app.route("/admin_comments",methods=['GET'])
def admin_comments():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ratings")
        comments = cursor.fetchall()
    return render_template('admin_comments.html',comments=comments)

# class Person(Model):
#     username = CharField()
#     fname = CharField()
#     lname = CharField()
#     pw = CharField()
#     email = CharField()
#     active = BooleanField()

#     class Meta:
#         database = db


# class Pet(Model):
#     person = ForeignKeyField(Person, related_name='pets')
#     petName = CharField()

#     class Meta:
#         database = db

# db.connect()

# if not (
# 	Person.table_exists() and Pet.table_exists()
# ):
# 	db.create_tables([Person,Pet], safe=True)


# testData = Person(username='hunter',pw='123q', fname='carls', lname='eriksen', email = 'email@email.com',active=True)
# testData.save()

# testData3 = Pet(person=testData,petName='dog')
# testData3.save()

# db.close()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0',port=1111)
