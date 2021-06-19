var useOrientationState = false;
var VELOCITY_FACTOR = 0.7;

/*
Velocity-based controller state.
Use this controller for laptops and non-mobile devices.
*/
var controllerState = {
  move_x: 0, // +1 -> right, -1 -> left
  move_y: 0, // +1 -> up, -1 -> down
  rev: false,
};

function clampControllerState() {
  if (controllerState.move_x < -1) controllerState.move_x = -1;
  if (controllerState.move_x > 1) controllerState.move_x = 1;
  if (controllerState.move_y < -1) controllerState.move_y = -1;
  if (controllerState.move_y > 1) controllerState.move_y = 1;
}

/*
Position/orientation-based controller state.
Use this controller for devices with orientation events enabled.
*/
var orientationState = {
  pan: 0.0, // horizontal rotation of turret, in [-90, +90].
  tilt: 0.0, // vertical rotation of turret, in [-90, +90].
};

function clampOrientationState() {
  if (orientationState.pan < -90) orientationState.pan = -90;
  if (orientationState.pan > 90) orientationState.pan = 90;
  if (orientationState.tilt < -90) orientationState.tilt = -90;
  if (orientationState.tilt > 90) orientationState.tilt = 90;
}

//MAIN BODY----------------------
function main() {
  var isFirefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
  useOrientationState = isFirefox;

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
    if (useOrientationState) {
      socket.emit("orientation_state", orientationState);
    } else {
      socket.emit("controller_state", controllerState);
    }
  }, 100);

  document.body.addEventListener("keydown", function (e) {
    switch (e.key) {
      case "ArrowLeft": {
        controllerState.move_x = -VELOCITY_FACTOR;
        break;
      }
      case "ArrowRight": {
        controllerState.move_x = VELOCITY_FACTOR;
        break;
      }
      case "ArrowUp": {
        controllerState.move_y = VELOCITY_FACTOR;
        break;
      }
      case "ArrowDown": {
        controllerState.move_y = -VELOCITY_FACTOR;
        break;
      }
      case "Control": {
        controllerState.rev = true;
        break;
      }
      case " ": {
        socket.emit("fire", {});
        break;
      }
      default: {
        // do nothing
        break;
      }
      clampControllerState();
    }
  });
  document.body.addEventListener("keyup", function (e) {
    switch (e.key) {
      case "ArrowLeft": {
        controllerState.move_x = 0;
        break;
      }
      case "ArrowRight": {
        controllerState.move_x = 0;
        break;
      }
      case "ArrowUp": {
        controllerState.move_y = 0;
        break;
      }
      case "ArrowDown": {
        controllerState.move_y = 0;
        break;
      }
      case "Control": {
        controllerState.rev = false;
        break;
      }
      default: {
        // do nothing
        break;
      }
      clampControllerState();
    }
  });
  window.addEventListener("deviceorientation", function(e) {
    document.getElementById("alpha").innerHTML = `alpha: ${e.alpha}`;
    document.getElementById("beta").innerHTML = `beta: ${e.beta}`;
    document.getElementById("gamma").innerHTML = `gamma: ${e.gamma}`;
    orientationState.pan = e.alpha;
    orientationState.tilt = e.beta + 90.0;
    clampOrientationState();
  });
}

window.onload = main;
