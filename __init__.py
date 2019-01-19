from flask import request, Flask, render_template, Markup, redirect, jsonify
from .database import engine, User, Token, Workspace, Note, Connection
from .error import MissingInformation, InvalidInformation
import sqlalchemy as db
from sqlalchemy import sql
from binascii import b2a_hex, a2b_hex
from hashlib import sha256
from os import urandom
import re

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


def login(username, password):
    hasher = sha256()
    hasher.update(password.encode("utf8"))
    passhash = hasher.digest()
    conn = engine.connect()
    query = sql.select([User.__table__]).where(
        (User.username == username.lower())
        & (User.passhash == passhash)
    )
    for row in conn.execute(query).fetchall():
        return row
    else:
        return None

def authenticate():
    token = request.cookies.get("token")
    if token is None:
        raise MissingInformation("token")
    token_bin = a2b_hex(token)
    conn = engine.connect()
    query = sql.select([Token.__table__])\
        .limit(1)\
        .where(Token.token == token_bin)
    row = conn.execute(query).fetchone()
    return row.user

# Return a list of all users workspaces
@app.route("/workspaces")
def get_workspaces():
    pass

# Create new workspace and return id
@app.route("/workspace/create/<name>")
def create_workspace(name):
    try:
        owner = authenticate()
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
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

# Return all nodes in workspace (list of notes and connections)
@app.route("/workspace/<int:id>")
def get_workspace(id):
    try:
        owner = authenticate()

        conn = engine.connect()

        # define query for db request to get all nodes for workspace id
        notes_query = sql.select([Note.__table__])\
            .where(Note.workspace == id)
        # define query for db request to get all nodes for workspace id
        connections_query = sql.select([Note.__table__])\
            .where(Note.workspace == id)

        notes = conn.execute(notes_query).fetchall()
        connections = conn.execute(connections_query).fetchall()

        workspace_notes = []
        for note in notes:
            workspace_notes.append({
                    "id": note.id,
                    "name": note.name
                })
        workspace_connections = []

        return jsonify({
                "status" : "ok",
                "notes" : workspace_notes
            })
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})


# Delete workspace and return id
@app.route("/workspace/delete/<int:id>")
def delete_workspace(id):
    pass

# Issue login token
@app.route("/token", methods=['POST'])
def get_token():
    try:
        username = request.form["username"]
        password = request.form["password"]
        if username is None:
            raise MissingInformation("username")
        if password is None:
            raise MissingInformation("password")
    except MissingInformation as e:
        return jsonify({ "status": "error", "message": e.message })
    username = username.lower()
    user = login(username, password)
    if user is None:
        return jsonify({"status": "error", "message": "Invalid login"})
    conn = engine.connect()
    query = sql.select([Token.__table__])\
        .limit(1)\
        .where(Token.id == user.id)
    res = conn.execute(query)
    row = res.fetchone()
    if row is None:
        hasher = sha256()
        hasher.update(urandom(16))
        token = hasher.digest()
        query = sql.insert(Token.__table__, values={
                Token.user: user.id,
                Token.token: token,
            })
        res = conn.execute(query)
        token_hex = b2a_hex(token).decode('ascii')
        return jsonify({"status": "ok", "token": token_hex});
    else:
        token_hex = b2a_hex(row.token).decode('ascii')
        return jsonify({"status": "ok", "token": token_hex});

# Create user
@app.route("/register", methods=['POST'])
def register():
    conn = engine.connect()
    try:
        username = request.form["username"]
        password = request.form["password"]
        if username is None:
            raise MissingInformation("username")
        if password is None:
            raise MissingInformation("password")
    except MissingInformation as e:
        return jsonify({ "status": "error", "message": e.message })

    try:
        username = username.lower()
        if len(username) < 3:
            raise InvalidInformation("username", "Must be at lest 3 characters.")
        if len(username) > 32:
            raise InvalidInformation("username", "Must be at most 32 characters.")
        if re.match("[^a-z0-9]", username):
            raise InvalidInformation("username", "Can only contain alphanumeric characters")
        query = sql.select([User.id]).where(User.username == username)
        res = conn.execute(query)
        if bool(len(res.fetchall())):
            raise InvalidInformation("username", "A user with that name already exists")
        if len(password) < 8:
            raise InvalidInformation("password", "Must be at least 8 characters")
        if len(password) > 32:
            raise InvalidInformation("password", "Must be at most 32 characters")
    except InvalidInformation as e:
        return jsonify({ "status": "error", "message": e.message })

    hasher = sha256()
    hasher.update(password.encode("utf8"))
    passhash = hasher.digest()
    query = sql.insert(User.__table__,
            values={
                User.username: username,
                User.passhash: passhash,
                }
            )
    res = conn.execute(query)
    return jsonify({ "status": "ok" })

# Create note in workspace
@app.route("/workspace/<int:id>/create/<name>")
def create_note(id, name):
    try:
        owner = authenticate()

        conn = engine.connect()
        query = sql.insert(Note.__table__,
                values={
                    Note.name: name,
                    Note.workspace: id
                    }
                )
        result = conn.execute(query)
        return jsonify({
                "status": "ok",
                "note": {
                    "id": result.lastrowid,
                    "name": name
                }
            })
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

# Connect two nodes
@app.route("/workspace/<int:id>/connect/<int:origin>/<int:target>")
def connect_notes(id, origin, target):
    pass

# Update note
@app.route("/workspace/<int:id>/update/<int:note>", methods=['GET', 'POST'])
def update_note(id, note):
    pass

# Remove note from workspace
@app.route("/workspace/<int:id>/remove/<int:note>")
def remove_note(id, note):
    pass

@app.route("/")
def index():
    return render_template('index.html')
