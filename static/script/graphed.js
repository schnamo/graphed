import {api} from '/static/script/api.js';

// api.registerUser("test", "testhello", function() {});

api.getToken("test", "testhello", function(token) {
  api.createWorkspace("creatingNew", function(workspace_id) {
    console.log(workspace_id);
    api.createNote(workspace_id, "blubber", function(note1) {
      console.log(note1);
      api.createNote(workspace_id, "tada", function(note2) {
        console.log(note2);
        api.createNote(workspace_id, "tralala", function(note3){
          console.log(note3);
          api.connectNotes(workspace_id, note1.id, note2.id, function(connection) {
            console.log(connection);
            api.connectNotes(workspace_id, note2.id, note3.id, function(connection) {
              console.log(connection);
                api.getWorkspace(workspace_id, function(workspaceStuff) {
                  console.log(workspaceStuff);
                  api.removeNote(workspace_id, note3.id, function() {
                    api.getWorkspace(workspace_id, function(workspaceStuff2) {
                      console.log(workspaceStuff2);
                  });
                });
              });
            });
          });
        });
      });
    });
  });
});
