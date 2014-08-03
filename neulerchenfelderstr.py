# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# create our little application :)
app = Flask(__name__)
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

#############
""" VIEWS """
#############

@app.route('/')
def index():

    db = get_db()
    cur = db.execute('SELECT f, nummer FROM images ORDER BY f')
    images = cur.fetchall()
    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run()