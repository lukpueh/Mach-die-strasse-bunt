#####################
""" IMPORTS """
#####################
import os

import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta
from time import time
from flask import (Flask, request, session, g, redirect, url_for, abort,
     render_template, flash, jsonify, make_response, send_from_directory)
from flask_login import (LoginManager, login_required, login_user,
                         current_user, logout_user, UserMixin)
from werkzeug.security import generate_password_hash, check_password_hash
from wand.image import Image

#####################
""" CONFIGURATION """
#####################

app = Flask(__name__, static_url_path='', instance_relative_config=True)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'neulerchenfelderstr.db'),
    DEBUG=True,
    USE_PIWIK=False,
    SECRET_KEY='12345devel', # Wow, you discovered a secret key. Good for you! This is overridden anyways. :P
    UPLOAD_FOLDER='drawings',
    IMAGE_FOLDER='img/regular',
    LOG_FILE=os.path.join(app.root_path, 'log/neulerchenfelderstr.log')
))

app.config.from_pyfile('config.py')

# Login Config
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Logger
file_handler = RotatingFileHandler(app.config['LOG_FILE'])
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s in %(funcName)s: %(message)s'))
app.logger.addHandler(file_handler)


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


#############
""" VIEWS """
#############
@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error("%s: Internal Error: %s", request.remote_addr, str(e))
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    app.logger.error("%s: Page not Found: %s", request.remote_addr, request.path)
    return render_template('404.html'), 404

@app.route('/')
def index():
    return redirect(url_for('draw'))

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

@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

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
        res['imagefile'] = url_for('static',
                filename=os.path.join(
                app.config["IMAGE_FOLDER"], image['file']))

        if (drawingid is not None):
            if current_user.is_authenticated:
                drawing = query_db('SELECT file FROM drawings WHERE id = ?', [drawingid], one=True)
            else:
                drawing = query_db('SELECT file FROM drawings WHERE is_approved = 1 AND id = ?', [drawingid], one=True)

            res['drawingfile'] = url_for('static', filename=os.path.join(
                    app.config["UPLOAD_FOLDER"], drawing['file']))

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
            with open(os.path.join(app.root_path,
                    app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
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

    timestamp = time()
    to_approve = request.form.getlist("do_approve")
    approved = query_db('SELECT id from drawings WHERE is_approved = 1')
    to_disapprove = []

    # Disapprove drawings that are
    for drawing in approved:
        if unicode(drawing['id']) not in to_approve:
            to_disapprove.append(drawing['id'])

    len_to_approve = len(to_approve)
    len_to_disapprove = len(to_disapprove)

    # Update Database (injection safe :))
    if len_to_approve:
        insert_db('UPDATE drawings SET is_approved = 1, ts_moderated = ? WHERE is_approved = 0 AND ' + ' OR '.join(['id = ?'] * len_to_approve), [str(timestamp)] + to_approve)
    if len_to_disapprove:
        insert_db('UPDATE drawings SET is_approved = 0, ts_moderated = ? WHERE is_approved = 1 AND ' + ' OR '.join(['id = ?'] * len_to_disapprove), [str(timestamp)] + to_disapprove)


    return redirect(url_for('admin'))

@app.route('/getfile', methods=['GET'])
@login_required
def get_file():
    try:
        drawingid = request.args.get('drawingid')
        imageid = request.args.get('imageid')

        image = query_db('SELECT file FROM images WHERE  id = ?', [imageid], one=True)
        drawing = query_db('SELECT file FROM drawings WHERE id = ?', [drawingid], one=True)

        with Image(filename=os.path.join(app.root_path, "static", app.config['IMAGE_FOLDER'], image['file'])) as img:
            with Image(filename=os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], drawing['file'])) as drw:
                img.resize(700, 495)
                img.composite(drw, left=0, top=0)
                body = img.make_blob()

        resp =  make_response(body)
        resp.headers['Content-Disposition'] = "attachment; filename=%s.png" % drawing['file']
        return resp

    except Exception, e:
        app.logger.error("%s: Exception: %s", request.remote_addr, str(e))


@app.route('/drawings/<path:filename>')
def drawings(filename):
    drawing = query_db('SELECT is_approved FROM drawings WHERE file = ?',
            [filename], one=True)

    if (drawing is not None and
            (drawing["is_approved"] or current_user.is_authenticated)):

        return send_from_directory(
            os.path.join(app.root_path, app.config['UPLOAD_FOLDER']),
            filename
        )

    else:
        abort(404)


if __name__ == '__main__':
    app.run()
