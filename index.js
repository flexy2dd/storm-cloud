//var Gpio = require('onoff').Gpio; //require onoff to control GPIO
//var LEDPin = new Gpio(4, 'out'); //declare GPIO4 an output
var fs = require('fs'); //require filesystem to read html files
var http = require('http').createServer(function handler(req, res) { //create server
  fs.readFile(__dirname + '/index.html', function (err, data) { //read html file
    if (err) {
      res.writeHead(500);
      return res.end('Error loading socket.io.html');
    }

    res.writeHead(200);
    res.end(data);
  });
});

var io = require('socket.io')(http) //require socket.io module and pass the http object

http.listen(8080, () => {
  console.log('listening on *:8080');
});

io.sockets.on('connection', function (socket) {// WebSocket Connection
  var buttonState = 0; //variable to store button state

  socket.on('state', function (data) { //get button state from client
    buttonState = data;
//    if (buttonState != LEDPin.readSync()) { //Change LED state if button state is changed
//      LEDPin.writeSync(buttonState); //turn LED on or off
//    }
  });
});