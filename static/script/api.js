function attemptAPIGetRequest(url, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == XMLHttpRequest.DONE) {
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
  xhttp.send();
}

export var api = {
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
  }
};
