import sqlite3
from flask import Flask, render_template, json, request, g
app = Flask(__name__)
DATABASE = './test.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))
    db.row_factory = make_dicts
    return db


def commit_db():
    get_db().commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def create_testdb():
    query_db("drop table if exists tbl_user")
    query_db('CREATE TABLE tbl_user (user_id integer primary key AUTOINCREMENT, user_name VARCHAR(45) NULL, user_username VARCHAR(45) NULL, user_password VARCHAR(45) NULL)')
    # for user in query_db('select * from tbl_user'):
    #     print(user['user_username'], 'has the id', user['user_id'])
    query_db("insert into tbl_user(user_name,user_username,user_password) values('Vijayamanikandan Rajaguru','vijay','admin')")
    query_db("insert into tbl_user(user_name,user_username,user_password) values('Thomas A Anderson','neo','theone')")
    query_db("insert into tbl_user(user_name,user_username,user_password) values('Smith','smith','iamnotabot')")
    commit_db()


@app.route('/')
@app.route('/index')
@app.route('/main')
def main():
    return render_template("index.html")


@app.route("/showSignUp")
def showsignup():
    return render_template("signup.html")


@app.route('/signUp', methods=['POST'])
def signUp():
    # create_testdb()
    # read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    # validate the received values
    if _name and _email and _password:
        if len(query_db('select * from tbl_user where user_username=?', [_email])) == 0:
            query_db("insert into tbl_user(user_name,user_username,user_password) values(?,?,?)", [_name, _email, _password])
            commit_db()
        else:
            return json.dumps({'error': 'User already exists!'})
        # for user in query_db('select * from tbl_user'):
        #     print(user['user_username'], 'has the id', user['user_id'])
        return json.dumps({'message': 'User created successfully!', 'users': query_db('select user_id, user_username from tbl_user')})
    else:
        return json.dumps({'error': 'Fields cannot be empty!'})


if __name__ == '__main__':
    app.run(debug=True)
