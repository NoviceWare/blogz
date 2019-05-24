from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import MEDIUMTEXT

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:hello@localhost/build-a-blog?unix_socket=/var/lib/mysql/mysql.sock' 
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class BlogEntry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1024))
    body = db.Column(db.Text())

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        errors = 0
        if not title:
            flash('Post title is required', 'titleerror')
            errors += 1
        if not body:
            flash('Post body is required', 'bodyerror')
            errors += 1
        if errors > 0:
            return render_template('newpost.html')
        new_post = BlogEntry(title, body)
        db.session.add(new_post)
        db.session.commit()
        id = new_post.id
        return redirect('/blog?id={}'.format(id))
    else:
        return render_template('newpost.html')
    return redirect('/blog')

@app.route('/blog')
def blog():
    id = request.args.get('id')
    if id: 
        posts = BlogEntry.query.filter_by(id=int(id)).all()
    else:
        posts = BlogEntry.query.all()

    return render_template('blog.html',title="Blogorama!", posts=posts)

@app.route('/')
def index():
    return render_template('base.html',title="Blogorama!")

app.secret_key = "DSGASDT#QWE#WERTWETWETWE@#$@#$"

if __name__ == '__main__':
    app.run()
