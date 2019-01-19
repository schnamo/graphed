import {api} from '/static/script/api.js';

// api.registerUser("test", "testhello", function() {});

api.getToken("test", "testhello", function(token) {
  api.createWorkspace("creating", function(id) {
    console.log(id);
    api.createNote(id, "blubber", function(note) {
      console.log(note);
    });
    api.createNote(id, "tada", function(note) {
      console.log(note);
    });
  });
});
