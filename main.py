from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:hello@localhost/blogz?unix_socket=/var/lib/mysql/mysql.sock' 
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(25))
    password = db.Column(db.String(25))
    email = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, login, password, email):
        self.login = login
        self.password = password
        self.email = email

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1024))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'login' not in session:
        return redirect('/login')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

def check_string(string):
    if string.find(" ") != -1 or len(string) < 3 or len(string) > 20:
        return False
    else:
        return True

def check_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        
        if user:
            if user.password == password:
                session['login'] = login
                flash("Logged in")
                return redirect('/newpost')
            else:
                flash('User password incorrect', 'loginerror')
        else:
            flash('Account does not exist', 'loginerror')
    else:
        redirect('/newpost')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        errors = 0
        #Verify login
        if login:
            if check_string(login) == False:
                flash('login reqs: alphanumeric and between 3-20 characters', 'loginerror')
                errors += 1
        else:
            flash('login is required', 'loginerror')
            errors += 1

        # Verify passwords
        if password and verify:
            if password != verify:
                flash('passwords did not match', 'passworderror')
                errors += 1
            else:
                if check_string(password) == False:
                    flash('password reqs: alphanumeric and between 3-20 characters', 'passworderror')
                    errors += 1
        else:
            flash('password and verification is required', 'passworderror')
            errors += 1

        # Verify email
        if email:
            if check_email(email) == False:
                flash(email + ' is not a valid email address', 'emailerror')
                errors += 1

        if errors == 0:
            existing_user = User.query.filter_by(login=login).first()
            if not existing_user:
                new_user = User(login, password, email)
                db.session.add(new_user)
                db.session.commit()
                session['login'] = login
                return redirect('/newpost')
            else:
                flash('Account already exists', 'loginerror')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['login']
    return redirect('/blog')

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
        writer = User.query.filter_by(login=session['login']).first()
        new_post = Blog(title, body, writer)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_post.id))
    else:
        return render_template('newpost.html')
    return redirect('/blog')

@app.route('/blog')
def blog():
    id = request.args.get('id')
    userid = request.args.get('userid')
    if userid: 
        posts = Blog.query.filter_by(owner_id=int(userid)).all()
        return render_template('singleUser.html',title="Blogz!", posts=posts)
    elif id:
        posts = Blog.query.filter_by(id=id).all()
        return render_template('blog.html',title="Blogz!", posts=posts)

    posts = Blog.query.all()
    return render_template('blog.html',title="Blogz!", posts=posts)

@app.route('/', methods = ['GET', 'POST'])
def index():
    authors = User.query.order_by('login').all()
    return render_template('index.html',title="Blogz!", authors=authors)

app.secret_key = "DSGASDT#QWE#WERTWETWETWE@#$@#$"

if __name__ == '__main__':
    app.run()