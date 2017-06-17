/* Initial Gun Test

The circuit:
Pusher switch on pin 4
Acceleration motor relay input on pin 7
Firing motor relay input on pin 8
Manual input on pin 12

*/

#include <Servo.h>

#define REV_UP_TIME    300
#define MAX_TILT_UP   2000
#define MAX_TILT_DOWN 1300
#define MAX_PAN_LEFT   800
#define MAX_PAN_RIGHT 2200
#define TILT_MIDPOINT 1500
#define PAN_MIDPOINT  1455

const int pusherSwitchPin      =  4;
const int accelerationMotorPin =  7;
const int pusherMotorPin       =  8;
const int tiltServoPin         = 10;
const int panServoPin          = 11;
const int buttonPin            = 12;
const int ledPin               = 13;

const char startCode = 's';
const char waitCode = 'w';
const char revCode = 'r';
const char fireCode = 'f';
const char tiltCode = 't';
const char panCode =  'p';
const char endCode = 'e';
const char errorCode = 'x';

const int startAutoFireCode = 65535;
const int stopAutoFireCode = 0;

unsigned long startTime;
int serialAction;
unsigned int serialParameter;
String s;
// PWM range 556-2420 => 1488
Servo panServo;
Servo tiltServo;

bool withinRange(int var, int low, int high) {
    return low <= var && var <= high;
}

void revUp() {
    digitalWrite(accelerationMotorPin, LOW);
}

void revDown() {
    digitalWrite(accelerationMotorPin, HIGH);
}

void pusherOn() {
    digitalWrite(pusherMotorPin, LOW);
}

void pusherOff() {
    digitalWrite(pusherMotorPin, HIGH);
}

void pulsePusher() {
    pusherOn();
    delay(15);
    pusherOff();
    delay(80);
}

void resetPusher() {
    pusherOff();
    while (digitalRead(pusherSwitchPin) == HIGH) pulsePusher();
}

void pan(int location) {
    if (withinRange(location, MAX_PAN_LEFT, MAX_PAN_RIGHT)) {
        panServo.writeMicroseconds(location);
    }
    else {
        Serial.println("Pan location out of range!");
    }
}

void tilt(int location) {
    if (withinRange(location, MAX_TILT_DOWN, MAX_TILT_UP)) {
        tiltServo.writeMicroseconds(location);
    } else {
        Serial.println("Tilt location out of range!");
    }
}

void rev(int argument) {
    if (argument == 0) {
        revDown();
    } else if (argument == 65535) {
        revUp();
    } else {
        Serial.println("Bad rev argument!");
    }
}

void fire(int argument) {
    if (withinRange(numShots, 1, 37)) {
        fireShots(argument)
    } else if (argument == 0) {
        resetPusher();
    } else if (argument == 65535) {
        pusherOn();
    } else {
        Serial.println("Inproper number of shots received!");
    }
}

void fireShots(int numShots) {
    startTime = millis();
    revUp();
    while (millis() - startTime < REV_UP_TIME);
    for ( ; numShots > 0; numShots--) {
        while (digitalRead(pusherSwitchPin) == LOW) pulsePusher();
        while (digitalRead(pusherSwitchPin) == HIGH) pulsePusher();
    }
    revDown();
}

byte getNextByte() {
    do {
        serialAction = Serial.read();
    } while (serialAction == -1);
    return byte(serialAction);
}

void waitForInput() {
    Serial.write('w');
    byte start = getNextByte();
    if (start != startCode) {
        Serial.println("Invalid start byte");
        return;
    }
    byte actionCode = getNextByte();
    // Serial.write(actionCode);
    int parameter = (int(getNextByte()) << 8) + int(getNextByte());
    // Serial.println(parameter);
    byte end = getNextByte();
    if (end != endCode) {
        Serial.println("Invalid start byte");
        return;
    }
    switch (actionCode) {
        case fireCode:
            fire(parameter);
            break;
        case tiltCode:
            tilt(parameter);
            break;
        case panCode:
            pan(parameter);
            break;
        case revCode:
            rev(parameter);
            break;
        default:
            Serial.println("Invalid action code");
    }
}

// void verifyComms() {
//     do {
//         Serial.println("Waiting for a verification message...");
//         do {
//             serialAction = Serial.read();
//         } while (serialAction == -1);
//         Serial.println("Please send 1500...");
//         do {
//             s = Serial.readString();
//             serialParameter = s.toInt();
//         } while (serialParameter == 0);
//     } while (serialAction != 'v' || serialParameter != 1500);
// }

void setup() {
    Serial.begin(9600);
    pinMode(pusherSwitchPin, INPUT_PULLUP);
    pinMode(accelerationMotorPin, OUTPUT);
    pinMode(pusherMotorPin, OUTPUT);
    pinMode(buttonPin, INPUT_PULLUP);
    pinMode(ledPin, OUTPUT);
    panServo.attach(panServoPin);
    tiltServo.attach(tiltServoPin);
    pan(PAN_MIDPOINT);
    tilt(TILT_MIDPOINT);
    revDown();
    resetPusher();
}

void loop() {
    waitForInput();
}
