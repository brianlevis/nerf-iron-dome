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
}

window.onload = main;
