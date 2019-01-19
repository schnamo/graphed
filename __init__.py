from flask import request, Flask, render_template, Markup, redirect, jsonify

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Create new workspace and return id
@app.route("/workspace/create/<name>")
def create_workspace(name):
    return jsonify({ "status": "ok" })

# Return all nodes in workspace (list of notes)
@app.route("/workspace/<id>")
def get_workspace(id):
    pass

# Create new workspace and return id
@app.route("/workspace/delete/<id>")
def delete_workspace(id):
    pass

# Issue login token
@app.route("/token", methods=['GET', 'POST'])
def user_login():
    pass

# Create note in workspace
@app.route("/workspace/<id>/create/")
def create_note(id):
    pass

# Connect two nodes
@app.route("/workspace/<id>/connect/<origin>/<target>")
def connect_notes(id, origin, target):
    pass

# Update note
@app.route("/workspace/<id>/update/<note>", methods=['GET', 'POST'])
def update_note(id, note):
    pass

# Remove note from workspace
@app.route("/workspace/<id>/remove/<note>")
def remove_note(id, note):
    pass

@app.route("/")
def index():
    return render_template('index.html')
