#app.py
from distutils.command.config import config
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,request,make_response

import psycopg2 #pip install psycopg2 
import datetime
import psycopg2.extras
import jwt

from functools import wraps
 
app = Flask(__name__)
app.secret_key = "cairocoders-ednalan"

app.config['SECRET_KEY'] = 'thisisthesecretkey'
 
DB_HOST = "localhost"
DB_NAME = "abcd"
DB_USER = "postgres"
DB_PASS = "123"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)



def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({"message": " Token is missing"}) , 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])

        except:
            return jsonify({"Message":" Token is invalid"}) , 403

        return f(*args,**kwargs)

    return decorated


@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == "123":
        token = jwt.encode({'user' : auth.username , 'exp': datetime.datetime.utcnow()  + datetime.timedelta(minutes=30)} , app.config['SECRET_KEY'])

        return jsonify({'token': token})

    return make_response('Could not verify!' , 401 ,{"WWW-authenticate" : 'Basic Realm = "Login required"'})
       

 
@app.route('/')
@token_required
def Index():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM students"
    cur.execute(s) # Execute the SQL
    list_users = cur.fetchall()
    return render_template('index.html', list_users = list_users)
 
@app.route('/add_student', methods=['POST'])
def add_student():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        cur.execute("INSERT INTO students (fname, lname, email) VALUES (%s,%s,%s)", (fname, lname, email))
        conn.commit()
        flash('Student Added successfully')
        return redirect(url_for('Index'))
 
@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_employee(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM students WHERE id = {0}'.format(id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', student = data[0])
 
@app.route('/update/<id>', methods=['POST'])
def update_student(id):
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE students
            SET fname = %s,
                lname = %s,
                email = %s
            WHERE id = %s
        """, (fname, lname, email, id))
        flash('Student Updated Successfully')
        conn.commit()
        return redirect(url_for('Index'))
 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_student(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM students WHERE id = {0}'.format(id))
    conn.commit()
    flash('Student Removed Successfully')
    return redirect(url_for('Index'))
 
if __name__ == "__main__":
    app.run(debug=True)

    
# </string:id></id></id>