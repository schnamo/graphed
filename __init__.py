from flask import request, Flask, render_template, Markup, redirect, jsonify
from .database import engine, User, Token, Workspace, Note, Connection
from .error import MissingInformation, InvalidInformation
import sqlalchemy as db
from sqlalchemy import sql

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

def cookie_to_user(token):
    return 0

# Create new workspace and return id
@app.route("/workspace/create/<name>")
def create_workspace(name):
    token = request.cookies.get("token")
    owner = cookie_to_user(token)

    conn = engine.connect()
    query = sql.insert(Workspace.__table__,
            values={
                Workspace.name: name,
                Workspace.owner: owner
                }
            )
    result = conn.execute(query)
    return jsonify({
            "status": "ok",
            "id": result.lastrowid,
        })

# Return all nodes in workspace (list of notes)
@app.route("/workspace/<id>")
def get_workspace(id):
    token = request.cookies.get("token") # get token
    owner = cookie_to_user(token)

    conn = engine.connect()

    notes_query = sql.select([Note.__table__])\ # define query for db request to get all nodes for workspace id
        .where(Note.workspace == id)
    connections_query = sql.select([Note.__table__])\ # define query for db request to get all nodes for workspace id
        .where(Note.workspace == id)

    notes = conn.execute(notes_query).fetchall()
    connections = conn.execute(connections_query).fetchall()

    workspace_notes = []
    for note in notes: # build nodes for json
        workspace_notes.append({
        "node" : note.id,
        "name" : note.name,
        })
    workspace_connections = []
    for connection in connections:
        workspace_connections.append({
        "origin" : connection.origin,
        "target" : connection.target,
        })

    return jsonify({
            "notes" : workspace_notes,
            "connections" : workspace_connections
        })


# Create new workspace and return id
@app.route("/workspace/delete/<id>")
def delete_workspace(id):
    pass

# Issue login token
@app.route("/token", methods=['POST'])
def get_token():
    pass

# Create user
@app.route("/register", methods=['POST'])
def register():
    pass

# Create note in workspace
@app.route("/workspace/<id>/create/<name>")
def create_note(id, name):
    token = request.cookies.get("token") # get token
    owner = cookie_to_user(token)

    conn = engine.connect()
    query = sql.insert(Note.__table__,
            values={
                Note.name: name,
                Workspace.owner: owner
                }
            )
    result = conn.execute(query)
    return jsonify({
            "status": "ok",
            "id": result.lastrowid,
        })

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
