// Rotary encoder init
// WARNING ! This is WIRINGPI pin numerotation !! please see https://fr.pinout.xyz/pinout/wiringpi#*
/*
const Rotary = require('raspberrypi-rotary-encoder');
const oRotary = new Rotary(
  29, // pin Clk, 
  28, // pin Dt, 
  27, // pin Switch
);
*/

var ip = getIPAddress();

// Screen init
var Screen = require('./lib/screen.js');
var screen = new Screen();
screen.init();
screen.sleep();

console.log('bar');
//var i2cBus = require('i2c-bus').openSync(1),
/*
var oled = require('oled-i2c-bus');
var font = require('oled-font-5x7');
var oled = new oled(
  require('i2c-bus').openSync(1),
  {
    width: 128,
    height: 64
  }
);
*/

/*
oled.clearDisplay();
oled.setCursor(1, 1);
oled.writeString(font, 1, 'Initialisation...', 1, true);
oled.setCursor(1, 10);
oled.writeString(font, 1, 'IP: ' + ip, 1, true);
*/
//var Gpio = require('onoff').Gpio; //require onoff to control GPIO
//var LEDPin = new Gpio(4, 'out'); //declare GPIO4 an output
var fs = require('fs'); //require filesystem to read html files
/*
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
*/

function getIPAddress() {
  var interfaces = require('os').networkInterfaces();
  for (var devName in interfaces) {
    var iface = interfaces[devName];

    for (var i = 0; i < iface.length; i++) {
      var alias = iface[i];
      if (alias.family === 'IPv4' && alias.address !== '127.0.0.1' && !alias.internal)
        return alias.address;
    }
  }
  return '0.0.0.0';
}

function exit() {
  screen.cls();
  screen.off();
  process.exit();
}

process.on('SIGINT', exit);