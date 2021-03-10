
//var Gpio = require('onoff').Gpio
//import EventEmitter from 'events';
//import { DigitalInput, PULL_UP, PULL_DOWN, PULL_NONE } from 'raspi-gpio';
//import { getPins } from 'raspi-board';
//import { Gpio } from 'onoff';
//var Gpio = require('onoff').Gpio

// Use this to set pin mode and pull resistor state
//var aPinSw = new Gpio(16, 'in', 'both');
//var bPinDt = new Gpio(20,'in', 'both');
//var bPinClk = new Gpio(21, 'in', 'both');
const Rotary = require('raspberrypi-rotary-encoder');

// WARNING ! This is WIRINGPI pin numerotation !! please see https://fr.pinout.xyz/pinout/wiringpi#*
const pinClk = 29;// 21;
const pinDt = 28; // 20;
const pinSwitch = 27; // 16;

const rotary = new Rotary(pinClk, pinDt, pinSwitch);

rotary.on("rotate", (delta) => {
  console.log("Rotation :"+delta);
});
rotary.on("pressed", () => {
  console.log("Rotary switch pressed");
});
rotary.on("released", () => {
  console.log("Rotary switch released");
});

function exit() {
//  aPinSw.unexport();
//  bPinDt.unexport();
  rotary.unexport();
  process.exit();
}

process.on('SIGINT', exit);