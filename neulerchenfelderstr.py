#####################
""" IMPORTS """
#####################
import os
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta
from time import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from flask_login import (LoginManager, login_required, login_user, 
                         current_user, logout_user, UserMixin)
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, \
     check_password_hash

#####################
""" CONFIGURATION """
#####################

app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'neulerchenfelderstr.db'),
    DEBUG=True,
    SECRET_KEY='12345devel',
    UPLOAD_FOLDER=os.path.join(app.root_path, 'static/drawings/'),
    REMEMBER_COOKIE_DURATION=timedelta(days=14),
    LOG_FILE=os.path.join(app.root_path, 'log/combined.log')
))

login_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
login_manager = LoginManager()

# DON'T forget to set the envvar!!!
app.config.from_envvar('NEULERCHENFELDERSTR_PROD_CFG', silent=True)


################
""" DATABASE """
################

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        with app.open_resource('insert.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def create_user(shortname, name, password):
    with app.app_context():
        pw = hash_pass(password)
        insert_db('INSERT INTO users (shortname, name, password) VALUES(?,?,?)', [shortname, name, pw])

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def insert_db(query, args=()):
    db = get_db()
    db.cursor().execute(query, args)
    db.commit()
    # return if it worked

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#############
""" MODEL """
#############
class User(UserMixin):
    def __init__(self, shortname, name, password):
        self.shortname = shortname
        self.name = name
        self.password = password
 
    def get_auth_token(self):
        data = [str(self.shortname), self.password]
        return login_serializer.dumps(data)

    def get_id(self):
        return unicode(self.shortname)
 
    @staticmethod
    def get(name):
        user = query_db('SELECT shortname, name, password FROM users WHERE shortname = ?', [name], True)
        if user is not None:
            return User(user['shortname'], user['name'], user['password'])
        return None

#############
""" HELPERS """
#############
def hash_pass(password):
    return generate_password_hash(password)

def check_password(user, password):
    return check_password_hash(user.password, password)

@login_manager.user_loader
def load_user(shortname):
    return User.get(shortname)

@login_manager.token_loader
def load_token(token):
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()
    #Decrypt the Security Token, data = [username, hashpass] and get user
    data = login_serializer.loads(token, max_age=max_age)
    user = User.get(data[0])

    #Check Password and return user or None
    if user and check_password(user, data[1]):
        return user
    return None
    
#############
""" VIEWS """
#############
@app.route('/draw')
def draw():
    images = query_db('SELECT id, file FROM images ORDER BY id')
    return render_template('draw.html', images=images)

@app.route('/gallery')
def gallery():
    drawings = query_db('SELECT d.id, d.file, d.is_approved, d.image, i.file AS imagefile FROM drawings d INNER JOIN images i ON d.image = i.id WHERE is_approved = 1 ORDER BY ts_created DESC')
    return render_template('gallery.html', drawings=drawings)

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/admin')
@login_required
def admin():
    drawings = query_db('SELECT d.id, d.file, datetime(d.ts_created, \'unixepoch\', \'localtime\') AS ts_created, d.is_approved, d.image, i.file AS imagefile, d.creator_mail FROM drawings d INNER JOIN images i ON d.image = i.id ORDER BY ts_created DESC')
    return render_template('admin.html', drawings=drawings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.get(request.form['username'])        
        if user and check_password(user, request.form['password']):
            login_user(user, remember=True)
            return redirect(url_for('admin'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('draw'))

@app.route('/')
def index():
    return redirect(url_for('draw'))


@app.route('/changeimage', methods=['GET'])
def change_image():
    """Receives an imageid and a drawing id. Returns the url of both.
    If user is not logged in, only drawings that are approved are returned."""

    fileurl = ""
    res = {}
    try:
        drawingid =  request.args.get('drawingid')
        imageid = request.args.get('imageid')

        image = query_db('SELECT file FROM images WHERE  id = ?', [imageid], one=True)
        res['imagefile'] = url_for('static', filename='img/regular/' + image['file'] )

        if (drawingid is not None):
            if current_user.is_authenticated():
                drawing = query_db('SELECT file FROM drawings WHERE id = ?', [drawingid], one=True)
            else:
                app.logger.warning("Unauthenticated wants unapproved image")
                drawing = query_db('SELECT file FROM drawings WHERE is_approved = 1 AND id = ?', [drawingid], one=True)
            res['drawingfile'] = url_for('static', filename='drawings/' + drawing['file'] )

    except Exception, e:
        app.logger.error("%s: Exception: %s", request.remote_addr, str(e))

    return jsonify(res)

@app.route('/savedrawing', methods=['POST'])
def save_drawing():
    """Receives a base64 String (the drawing) and the email address of the drawer, 
    validates them and saves them to DB."""

    try:
        base64Str = request.form['drawing']
        base64List = base64Str.split(',')

        # Limit it to 8 MB - above is a bit fishy
        if len(base64List[1]) > 8388608:
            app.logger.warning("%s base64 too long", request.remote_addr)
            return jsonify(kind = "error")

        imageid = request.form['imageid']
        creatorMail = request.form['creatormail']

        # Email addresses can't be so long
        if len(creatorMail) > 254:
            app.logger.warning("%s IP too long", request.remote_addr)
            creatorMail = ""

        if base64List[0] == 'data:image/png;base64' and base64List[1] > 0:
            timestamp = time()
            filename = str(timestamp).replace('.', '_')
            with open(app.config['UPLOAD_FOLDER'] + filename, 'wb') as f:
                f.write(base64List[1].decode('base64'))

            insert_db('INSERT INTO drawings(file, ts_created, image, creator_mail) VALUES(?,?,?,?)', [filename, timestamp, imageid, creatorMail])
    
    except Exception, e:
        app.logger.error("%s: Exception: %s", request.remote_addr, str(e))
        return jsonify(kind = "error")
    else:
        return jsonify(kind = "success")

@app.route('/savemoderation', methods=['POST'])
@login_required
def save_moderation():
    """Updates the approved state (true or false) of drawings."""

    try:
        timestamp = time()
        to_approve = request.form.getlist("do_approve")
        approved = query_db('SELECT id from drawings WHERE is_approved = 1')
        to_disapprove = []

        # Disapprove drawings that are
        for drawing in approved:
            if unicode(drawing['id']) not in to_approve:
                to_disapprove.append(drawing['id'])

        # Update Database
        if len(to_approve):
            insert_db('UPDATE drawings SET is_approved = 1, ts_moderated = ' + str(timestamp) + ' WHERE is_approved = 0 AND ' + ' OR '.join(["id=" + str(i) for i in to_approve]))
        if len(to_disapprove):
            insert_db('UPDATE drawings SET is_approved = 0, ts_moderated = ' + str(timestamp) + ' WHERE is_approved = 1 AND ' + ' OR '.join(["id=" + str(i) for i in to_disapprove]))
    except Exception, e:
        app.logger.error("%s: Exception: %s", request.remote_addr, str(e))

    return redirect(url_for('admin'))
        
if __name__ == '__main__':
    login_manager.login_view = "/login"
    login_manager.setup_app(app)

    file_handler = RotatingFileHandler(app.config['LOG_FILE'])
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s in %(funcName)s: %(message)s'))
    app.logger.addHandler(file_handler)

    app.run()