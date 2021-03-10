const Rotary = require('raspberrypi-rotary-encoder');

// WARNING ! This is WIRINGPI pin numerotation !! please see https://fr.pinout.xyz/pinout/wiringpi#*
const pinClk = 29;// 21;
const pinDt = 28; // 20;
const pinSwitch = 27; // 16;

const rotary = Rotary(pinClk, pinDt, pinSwitch);

var i2c = require('i2c-bus'),
  i2cBus = i2c.openSync(1),
  oled = require('oled-i2c-bus'),
  font = require('oled-font-5x7');

var opts = {
  width: 128,
  height: 64
};

var oled = new oled(i2cBus, opts);


oled.clearDisplay();
//oled.fillRect(1, 1, 10, 20, 1);
oled.setCursor(1, 1);
oled.writeString(font, 1, 'Cats and dogs are really cool animals, you know.', 1, true);

rotary.on("rotate", (delta) => {
  console.log("Rotation :"+delta);
});
rotary.on("pressed", () => {
  console.log("Rotary switch pressed");
});
rotary.on("released", () => {
  console.log("Rotary switch released");
});

console.log(getIPAddress());

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
  oled.clearDisplay();
  oled.turnOffDisplay();
  process.exit();
}

process.on('SIGINT', exit);