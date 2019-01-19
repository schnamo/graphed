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
    attemptAPIGetRequest("/workspaces",
                         function(data) { callback(data.workspaces); });
  },
  createWorkspace : function(name, callback) {
    attemptAPIGetRequest("/workspace/create/" + name,
                         function(data) { callback(data.id); });
  },
  getWorkspace : function(id, callback) {
    attemptAPIGetRequest("/workspace/" + id,
                         function(data) { callback(data.notes); });
  },
  deleteWorkspace : function(id, callback) {
    attemptAPIGetRequest("/workspace/" + id, function(data) { callback(); });
  },
  createNote : function(id, note, callback) {
    attemptAPIGetRequest("/workspace/" + id + "/create/",
                         function(data) { callback(data.note); });
  },
  connectNotes : function(id, origin, target, callback) {
    attemptAPIGetRequest(
        "/workspace/" + id + "/connect/" + origin + "/" + target,
        function(data) { callback(data.origin, data.target); });
  },
  updateNote : function(id, note, callback) {
    attemptAPIGetRequest("/workspace/" + id + "/update/" + note,
                         function(data) { callback(); });
  },
  removeNote : function(id, note, callback) {
    attemptAPIGetRequest("/workspace/" + id + "/remove/" + note,
                         function(data) { callback(); });
  },
  registerUser : function(username, password, callback) {
    attemptAPIPostRequest("/register",
                          {username : username, password : password},
                          function(data) { callback(); });
  },
  getToken : function(username, password, callback) {
    attemptAPIPostRequest("/token", {username : username, password : password},
                          function(data) {
                            document.cookie = "token=" + data.token;
                            callback(data.token);
                          });
  }
};
