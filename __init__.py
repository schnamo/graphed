from flask import request, make_response, Flask, render_template, Markup, redirect, jsonify, redirect
from .database import engine, User, Token, Workspace, Note, Connection
from .error import MissingInformation, InvalidInformation
import sqlalchemy as db
from sqlalchemy import sql, update
from binascii import b2a_hex, a2b_hex
from hashlib import sha256
from os import urandom, path
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
    if row is not None:
        return row.user
    else:
        raise MissingInformation("valid credentials")

def check_owner(owner, workspace_id):
    conn = engine.connect()
    workspace_query = sql.select([Workspace.__table__])\
                .where(Workspace.id == workspace_id)
    result = conn.execute(workspace_query)
    workspace = result.fetchone()
    if workspace is not None:
        return workspace.owner == owner
    else:
        return False

# Return a list of all users workspaces
@app.route("/api/workspaces")
def get_workspaces():
    try:
        owner = authenticate()

        conn = engine.connect()

        # define query for db  request to get workspaces
        workspace_query = sql.select([Workspace.__table__])\
            .where(Workspace.owner == owner)

        workspaces = conn.execute(workspace_query).fetchall()

        workspace_list = []
        for workspace in workspaces:
            workspace_list.append({
                    "id": workspace.id,
                    "name": workspace.name
                })

        return jsonify({
                "status" : "ok",
                "workspaces" : workspace_list
            })
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

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

# Update workspace name
@app.route("/api/workspace/<int:id>/rework/<name>")
def rename_workspace(id, name):
    try:
        owner = authenticate()
        if check_owner(owner, id):
            conn = engine.connect()
            query = sql.update(Workspace.__table__, values={Workspace.name: name}).where(Workspace.id == id)
            result = conn.execute(query)
            return jsonify({
                    "status": "ok",
                    "note": {
                        "id": id,
                        "name": name,
                    }
                })
        else:
            raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

# Return all notes and connections in workspace (list of notes)
@app.route("/api/workspace/<int:id>")
def get_workspace(id):
    try:
        owner = authenticate()
        if check_owner(owner, id):

            conn = engine.connect()

            # define query for db request to get all nodes for workspace id
            notes_query = sql.select([Note.__table__])\
                .where(Note.workspace == id)
            # define query for db request to get all nodes for workspace id
            connections_query = sql.select([Connection.__table__])\
                .where(Connection.workspace == id)

            notes = conn.execute(notes_query).fetchall()
            connections = conn.execute(connections_query).fetchall()

            workspace_notes = []
            for note in notes:
                workspace_notes.append({
                        "id": note.id,
                        "name": note.name
                    })
            workspace_connections = []
            for connection in connections:
                workspace_connections.append({
                        "id" : connection.id,
                        "origin" : connection.origin,
                        "target" : connection.target,
                    })

            return jsonify({
                    "status" : "ok",
                    "notes" : workspace_notes,
                    "connections" : workspace_connections,
                })
        else:
            raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})


# Delete workspace and return id
@app.route("/api/workspace/delete/<int:id>")
def delete_workspace(id):
    try:
        owner = authenticate()
        if check_owner(owner, id):

            conn = engine.connect()
            query = sql.delete(Note.__table__, Note.workspace == id)
            result = conn.execute(query)
            query = sql.delete(Connection.__table__, Connection.workspace == id)
            result = conn.execute(query)
            query = sql.delete(Workspace.__table__, Workspace.id == id)
            result = conn.execute(query)
            return jsonify({"status" : "ok", "message": "deleted"})
        else:
            raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

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

@app.route("/api/workspace/<int:id>/note/<int:note>")
def get_note(id, note):
    try:
        owner = authenticate()

        filename = "notes/" + str(note) + ".txt"
        if path.isfile(filename):
            with open(filename, 'r') as content_file:
                content = content_file.read()
                return jsonify({
                    "status" : "ok",
                    "content" : content,
                })
        else:
            return jsonify({"status": "error", "message": "No such note file"})
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})


# Create note in workspace
@app.route("/api/workspace/<int:id>/create/")
def create_note(id):
    try:
        owner = authenticate()
        if check_owner(owner, id):

            conn = engine.connect()
            query = sql.insert(Note.__table__,
                    values={
                        Note.name: "",
                        Note.workspace: id
                        }
                    )
            result = conn.execute(query)
            with open("notes/" + str(result.lastrowid) + ".txt", "w") as f:
                pass
            return jsonify({
                    "status": "ok",
                    "note": {
                        "id": result.lastrowid,
                        "name": ""
                    }
                })
        else:
            raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

# Connect two nodes
@app.route("/api/workspace/<int:id>/connect/<int:origin>/<int:target>")
def connect_notes(id, origin, target):
    try:
        owner = authenticate()
        if check_owner(owner, id):

            conn = engine.connect()
            if origin < target:
                origin_insert = origin
                target_insert = target
            elif origin > target:
                origin_insert = target
                target_insert = origin
            else:
                raise InvalidInformation("Note cannot reference to itself.")

            query = sql.insert(Connection.__table__,
                    values={
                        Connection.workspace: id,
                        Connection.origin: origin_insert,
                        Connection.target: target_insert,
                        }
                    )
            result = conn.execute(query)
            return jsonify({
                    "status": "ok",
                    "connection": {
                        "id": result.lastrowid,
                        "origin": origin_insert,
                        "target": target_insert,
                    }
                })
        else:
            raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

# Update note name
@app.route("/api/workspace/<int:id>/rename/<int:note>/<name>")
def rename_note(id, note, name):
    try:
        owner = authenticate()
        if check_owner(owner, id):

            conn = engine.connect()
            #db.update(table_name).values(attribute = new_value).where(condition)
            query = sql.update(Note.__table__, values={Note.name: name}).where(Note.id == note)
            # query = sql.update(Note.__table__)\
            #         .values(Note.name = name)\
            #         .where(Note.id == note)
            result = conn.execute(query)
            return jsonify({
                    "status": "ok",
                    "note": {
                        "id": note,
                        "name": name,
                    }
                })
        else:
            raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

# Update note
@app.route("/api/workspace/<int:id>/update/<int:note>", methods=['POST'])
def update_note(id, note):
    try:
        owner = authenticate()
        #if check_owner(owner, id):

        content = request.form["content"]
        filename = "notes/" + str(note) + ".txt"
        if path.isfile(filename):
            with open(filename, "w") as f:
                f.write(content)
                return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "message": "No such note"})
        #else:
        #    raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

# Remove note from workspace
@app.route("/api/workspace/<int:id>/remove/<int:note>")
def remove_note(id, note):
    try:
        owner = authenticate()
        if check_owner(owner, id):

            conn = engine.connect()

            # define query for db request to get all nodes for workspace id
            notes_query = sql.select([Note.__table__])\
                    .where(Note.workspace == id)
            notes = conn.execute(notes_query).fetchall()

            if len(notes) < 2:
                return jsonify({"status" : "ok", "message": "Not possible to remove last note in workspace"})
            else:
                query = sql.delete(Note.__table__, Note.id == note)
                result = conn.execute(query)
                query = sql.delete(Connection.__table__, Connection.origin == note)
                result = conn.execute(query)
                query = sql.delete(Connection.__table__, Connection.target == note)
                result = conn.execute(query)
                return jsonify({"status" : "ok", "message": "deleted"})
        else:
            raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

# Remove connection from workspace
@app.route("/api/workspace/<int:id>/disconnect/<int:connection>")
def remove_connection(id, connection):
    try:
        owner = authenticate()
        if check_owner(owner, id):

            conn = engine.connect()
            query = sql.delete(Connection.__table__, Connection.id == connection)
            result = conn.execute(query)
            return jsonify({"status" : "ok", "message": "deleted"})
        else:
            raise InvalidInformation("You don't have access to this workspace.")
    except MissingInformation as e:
        return jsonify({"status": "error", "message": e.message})

@app.route("/register")
def register():
    try:
        owner = authenticate()
        return redirect("/")
    except MissingInformation as e:
        return render_template('register.html')

@app.route("/logout")
def logout():
    resp = redirect('/')
    resp.set_cookie('token', '', expires=0)
    return resp

@app.route("/")
def index():
    authenticated = False
    try:
        owner = authenticate()
        authenticated = True
    except MissingInformation as e:
        pass
    return render_template('index.html', authenticated=authenticated)
