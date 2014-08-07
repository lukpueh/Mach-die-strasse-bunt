# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

# create our little application :)
app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)

#####################
""" CONFIGURATION """
#####################

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'neulerchenfelderstr.db'),
    DEBUG=True,
    SECRET_KEY='12345devel'
))

app.config.from_envvar('NEULERCHENFELDERSTR_SETTINGS', silent=True)

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

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#############
""" VIEWS """
#############

@app.route('/')
def index():
    images = query_db('SELECT f, file FROM images ORDER BY f')
    return render_template('index.html', images=images)

@app.route('/changeimage', methods=['GET'])
def change_image():

    fileurl = ""
    if request.method != 'GET':
        # Error Handling
        pass
    else:
        imageid = request.args.get('imageid')
        image = query_db('SELECT file FROM images WHERE f = ?', [imageid], one=True)
        if image is None:
            # Error Handling
            pass
        else:
            fileurl = url_for('static', filename='img/regular/' + image['file'] )

    return jsonify(file = fileurl)

@app.route('/savepainting', methods=['POST'])
def save_painting():
    if request.method != 'POST':
        # Error Handling
        pass
    else:
        print request.args.get('imageid')
        print request.args.get('painting')
        
if __name__ == '__main__':

    app.run()