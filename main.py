from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = '#secretkey'
db = SQLAlchemy(app)

class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(120))
    content = db.Column(db.Text())
    
    def __init__(self, name, content, owner):
        self.name = name
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogz = db.relationship('Entry', backref='owner') 

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():

    allowed_routes = ['login', 'register', 'index','entries']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/new_entry', methods=['GET'])
def new_entry():

    return render_template('/new.html')

@app.route('/new_entry', methods=['POST'])
def new_entry_2():

    new_entry_title = request.form['new_entry_title']
    new_entry_text = request.form['new_entry_text']
    owner = User.query.filter_by(username=session['username']).first()

    title_error = ''
    entry_error = ''

    if len(new_entry_title) < 1:
        title_error = "Please enter a title:)"
        
    if len(new_entry_text) < 1:
        entry_error = "Please fill your blog with content:)"

    if entry_error or title_error:

        return render_template('new.html', new_entry_title=new_entry_title,new_entry_text=new_entry_text, entry_error=entry_error, title_error=title_error)

    new_entry = Entry(new_entry_title, new_entry_text, owner)
    
    db.session.add(new_entry)
    db.session.commit()


    return redirect('/single?id={}'.format(new_entry.id))
     
    
@app.route('/single', methods=['GET'])
def single_entry():

    entry = int(request.args.get('id'))

    entry_id = Entry.query.filter_by(id=entry).first()
    entry_owner = entry_id.owner.username
    owner_id = entry_id.owner.id

    return render_template('single.html', entry_title=entry_id.name, entry_content=entry_id.content,
    entry_id=entry_id, entry_owner=entry_owner, owner_id=owner_id)

@app.route('/user', methods=['GET'])
def user():
    
    entry = int(request.args.get('id'))
    owner = User.query.filter_by(id=entry).first()

    entries = Entry.query.filter_by(owner_id=entry).all()

    return render_template('user.html',entries=entries, owner=owner)

@app.route('/', methods=['POST', 'GET'])
def entries():

    if request.method == 'GET':

        entries = Entry.query.all()
        return render_template('home.html', entries=entries)

    if request.method == 'POST':
        return redirect("/single")

@app.route('/signup',methods=['GET','POST'])
def register():

    username_error = ''
    password_error = ''

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        pass_conf = request.form['pass_conf']
        
        existing_user = User.query.filter_by(username=username).first()

        if username == '' or password == '' or pass_conf == '':
            flash("One or more fields is invalid.")
            return render_template('signup.html')
        
        if len(username) > 0 and len(username) < 3:
            username_error = 'Username cannot be less than 3 characters long'

        if len(password) > 0 and len(password) < 3:
            password_error = 'Password cannot be less than 3 characters long'

        if existing_user:
            flash("User already exists.")
            return render_template('signup.html')

        if username and password != pass_conf:
            flash("Passwords do not match.")
            return render_template('signup.html')

        if not username_error  and not password_error and not existing_user and password == pass_conf:
   
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("logged in")
            return redirect('/new_entry')

    return render_template("signup.html", username_error=username_error, password_error=password_error)

@app.route('/index', methods=['GET'])
def index():

    users = User.query.all()
    return render_template('index.html',users=users)

@app.route('/login', methods=['GET','POST'])
def login():

    password_error = ''
    username_error = ''
    username = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
       
        if user and user.password == password:
            session['username'] = username
            flash("logged in")
            return redirect('/new_entry')

        if user and user.password != password:
            session['username'] = username
            username = username
            password_error = 'Password is incorrect.'

        if not user:
            username = ''
            username_error = 'Username does not exist.'
        

    return render_template("login.html",password_error=password_error,username_error=username_error,username=username)

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()
