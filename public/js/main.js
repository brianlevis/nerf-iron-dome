var controllerState = {
  move_x: 0, // +1 -> right, -1 -> left
  move_y: 0, // +1 -> up, -1 -> down
  rev: false,
  fire: false,
};

//MAIN BODY----------------------
function main() {
  console.log("main loaded");
  var socket = io.connect();
  console.log("starting websocket connection");

  //send an explicit package to the server upon connection
  socket.on("connect",
    function(){
      console.log("Connection to WebSocket server being established");
      socket.emit("action_code", {code: 1});
    }
  );
  socket.on("disconnect",
    function() {
      console.log("Disconnected from WebSocket server");
    }
  );
  window.setInterval(function() {
    socket.emit("controller_state", controllerState);
  }, 100);

  document.body.addEventListener("keydown", function (e) {
    switch (e.key) {
      case "ArrowLeft": {
        controllerState.move_x -= 1;
        break;
      }
      case "ArrowRight": {
        controllerState.move_x += 1;
        break;
      }
      case "ArrowUp": {
        controllerState.move_y += 1;
        break;
      }
      case "ArrowDown": {
        controllerState.move_y -= 1;
        break;
      }
      default: {
        // do nothing
        break;
      }
    }
  });
  document.body.addEventListener("keyup", function (e) {
    switch (e.key) {
      case "ArrowLeft": {
        controllerState.move_x += 1;
        break;
      }
      case "ArrowRight": {
        controllerState.move_x -= 1;
        break;
      }
      case "ArrowUp": {
        controllerState.move_y -= 1;
        break;
      }
      case "ArrowDown": {
        controllerState.move_y += 1;
        break;
      }
      default: {
        // do nothing
        break;
      }
    }
  });
}

window.onload = main;
