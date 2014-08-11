# all the imports
import os
import time
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

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/drawings/')


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
""" VIEWS """
#############



@app.route('/draw')
def draw():
    images = query_db('SELECT id, file FROM images ORDER BY id')
    return render_template('draw.html', images=images)

@app.route('/gallery')
def gallery():
    drawings = query_db('SELECT d.id, d.file, d.ts_created, d.is_approved, d.image, i.file AS imagefile FROM drawings d INNER JOIN images i ON d.image = i.id WHERE is_approved = 1')
    return render_template('gallery.html', drawings=drawings)

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/admin')
def admin():
    drawings = query_db('SELECT d.id, d.file, d.ts_created, d.is_approved, d.image, i.file AS imagefile FROM drawings d INNER JOIN images i ON d.image = i.id')
    return render_template('admin.html', drawings=drawings)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('draw'))

@app.route('/')
def index():
    return redirect(url_for('draw'))

@app.route('/changeimage', methods=['GET'])
def change_image():

    fileurl = ""
    if request.method != 'GET':
        # Error Handling
        pass
    else:
        drawingid =  request.args.get('drawingid')
        imageid = request.args.get('imageid')

        print request.args
        image = query_db('SELECT file FROM images WHERE  id = ?', [imageid], one=True)
        res = {}
        res["imagefile"] = url_for('static', filename='img/regular/' + image['file'] )
        if (drawingid is not None):
            # only show not approved drawings when logged in

            drawing = query_db('SELECT file FROM drawings WHERE id = ?', [drawingid], one=True)
            res["drawingfile"] = url_for('static', filename='drawings/' + drawing['file'] )
        return jsonify(res)

@app.route('/savedrawing', methods=['POST'])
def save_drawing():
    if request.method != 'POST':
        # Error Handling
        pass
    else:
        base64Str = request.form['drawing']
        base64List = base64Str.split(',')
        imageid = request.form['imageid']
        if base64List[0] == 'data:image/png;base64' and base64List[1] > 0:
            timestamp = time.time()
            filename = str(timestamp).replace('.', '_')
            with open(app.config['UPLOAD_FOLDER'] + filename, 'wb') as f:
                f.write(base64List[1].decode('base64'))

            insert_db('INSERT INTO drawings(file, ts_created, image) VALUES(?,?,?)', [filename, timestamp, imageid])



    return jsonify(bla = "blub")
        
if __name__ == '__main__':

    app.run()