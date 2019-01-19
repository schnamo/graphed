from flask import request, Flask, render_template, Markup, redirect, jsonify, redirect
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

def check_credentials(username, password):
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
@app.route("/api/workspaces")
def get_workspaces():
    pass

# Create new workspace and return id
@app.route("/api/workspace/create/<name>")
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

# Return all nodes in workspace (list of notes)
@app.route("/api/workspace/<int:id>")
def get_workspace(id):
    pass

# Create new workspace and return id
@app.route("/api/workspace/delete/<int:id>")
def delete_workspace(id):
    pass

# Issue login token
@app.route("/api/token", methods=['POST'])
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
    user = check_credentials(username, password)
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
@app.route("/api/register", methods=['POST'])
def create_user():
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
@app.route("/api/workspace/<int:id>/create/")
def create_note(id):
    pass

# Connect two nodes
@app.route("/api/workspace/<int:id>/connect/<int:origin>/<int:target>")
def connect_notes(id, origin, target):
    pass

# Update note
@app.route("/api/workspace/<int:id>/update/<int:note>", methods=['GET', 'POST'])
def update_note(id, note):
    pass

# Remove note from workspace
@app.route("/api/workspace/<int:id>/remove/<int:note>")
def remove_note(id, note):
    pass

@app.route("/register")
def register():
    try:
        owner = authenticate()
        return redirect("/workspaces")
    except MissingInformation as e:
        return render_template('register.html')

@app.route("/")
def index():
    authenticated = False
    try:
        owner = authenticate()
        authenticated = True
    except MissingInformation as e:
        pass
    return render_template('index.html', authenticated=authenticated)

