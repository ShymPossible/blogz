from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.Text())
    

    def __init__(self, name, content):
        self.name = name
        self.content = content


@app.route('/new_entry', methods=['GET'])
def index():

    return render_template('/new.html')

@app.route('/new_entry', methods=['POST'])
def index_2():

    new_entry_title = request.form['new_entry_title']
    new_entry_text = request.form['new_entry_text']

    title_error = ''
    entry_error = ''

    if len(new_entry_title) < 1:
        title_error = "Please enter a title:)"
        
    if len(new_entry_text) < 1:
        entry_error = "Please fill your blog with content:)"

    if entry_error or title_error:

        return render_template('new.html', new_entry_title=new_entry_title,new_entry_text=new_entry_text, entry_error=entry_error, title_error=title_error)

    new_entry = Entry(new_entry_title, new_entry_text)
    
    db.session.add(new_entry)
    db.session.commit()


    return redirect('/single?id={}'.format(new_entry.id))
     
    
@app.route('/single', methods=['GET'])
def single_entry():

    entry = int(request.args.get('id'))

    entry_id = Entry.query.filter_by(id=entry).first()

    return render_template('single.html', entry_title=entry_id.name, entry_content=entry_id.content,
    entry_id=entry_id)

@app.route('/', methods=['POST', 'GET'])
def entries():

    if request.method == 'GET':
        entries = Entry.query.all()
        return render_template('home.html', entries=entries)

    if request.method == 'POST':
        return redirect("/single")


if __name__ == '__main__':
    app.run()
