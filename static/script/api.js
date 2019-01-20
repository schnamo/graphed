function attemptAPIGetRequest(url, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == XMLHttpRequest.DONE) {
      console.log(this.responseText);
      var response = JSON.parse(this.responseText);
      if (response.status == "ok") {
        if (callback !== undefined)
          callback(response);
      } else {
        console.log("API error");
      }
    }
  };
  xhttp.open("GET", url, true);
  xhttp.withCredentials = true;
  xhttp.send();
}

function attemptAPIPostRequest(url, data, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == XMLHttpRequest.DONE) {
      console.log(this.responseText);
      var response = JSON.parse(this.responseText);
      if (response.status == "ok") {
        if (callback !== undefined)
          callback(response);
      } else {
        console.log("API error");
      }
    }
  };
  var params = "";
  for (var property in data)
    params += property + "=" + data[property] + "&";
  params = params.substring(0, params.length - 1);
  xhttp.open("POST", url, true);
  xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
  xhttp.withCredentials = true;
  xhttp.send(params);
}

export var api = {
  getWorkspaces : function(callback) {
    attemptAPIGetRequest("/api/workspaces",
                         function(data) { callback(data.workspaces); });
  },
  createWorkspace : function(name, callback) {
    attemptAPIGetRequest("/api/workspace/create/" + name,
                         function(data) { callback(data.id); });
  },
  getWorkspace : function(id, callback) {
    attemptAPIGetRequest(
        "/api/workspace/" + id,
        function(data) { callback(data.notes, data.connections); });
  },
  deleteWorkspace : function(id, callback) {
    attemptAPIGetRequest("/api/workspace/delete/" + id,
                         function(data) { callback(); });
  },
  createNote : function(id, name, callback) {
    attemptAPIGetRequest("/api/workspace/" + id + "/create/" + name,
                         function(data) { callback(data.note); });
  },
  connectNotes : function(id, origin, target, callback) {
    attemptAPIGetRequest("/api/workspace/" + id + "/connect/" + origin + "/" +
                             target,
                         function(data) { callback(data.connection); });
  },
  removeConnection : function(id, connection, callback) {
    attemptAPIGetRequest("/api/workspace/" + id + "/disconnect/" + connection,
                         function(data) { callback(); });
  },
  getNote : function(id, note, callback) {
    attemptAPIGetRequest("/api/workspace/" + id + "/note/" + note,
                         function(data) { callback(data.content); });
  },
  updateNote : function(id, note, content, callback) {
    attemptAPIPostRequest("/api/workspace/" + id + "/update/" + note,
                          {content : content}, function(data) { callback(); });
  },
  removeNote : function(id, note, callback) {
    attemptAPIGetRequest("/api/workspace/" + id + "/remove/" + note,
                         function(data) { callback(); });
  },
  registerUser : function(username, password, callback) {
    attemptAPIPostRequest("/api/register",
                          {username : username, password : password},
                          function(data) { callback(); });
  },
  getToken : function(username, password, callback) {
    attemptAPIPostRequest("/api/token",
                          {username : username, password : password},
                          function(data) {
                            document.cookie = "token=" + data.token;
                            callback(data.token);
                          });
  }
};
