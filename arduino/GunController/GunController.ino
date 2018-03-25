#include <Servo.h>

/*
---------------------------------------------------------
                       Parameters
*/

#define REV_UP_TIME          300
#define MAX_FIRE_TIME       1000
#define MAX_TILT_UP         2000
#define MAX_TILT_DOWN       1300
#define MAX_PAN_LEFT         800
#define MAX_PAN_RIGHT       2200
#define TILT_MIDPOINT       1500
#define PAN_MIDPOINT        1455

#define ACCELERATION        1000
#define VELOCITY_MULTIPLIER    7
#define UPDATE_INTERVAL     2000

#define REV_UP_PERIOD         20
#define MAX_REV_DOWN_PERIOD  200

#define PUSHER_PULSE_ON_TIME  15
#define PUSHER_PULSE_OFF_TIME 80

/*
---------------------------------------------------------
                        Constants
*/

const int pusherSwitchPin      =  3;
const int accelerationMotorPin =  6;
const int pusherMotorPin       =  7;
const int tiltServoPin         = 10;
const int panServoPin          = 11;
const int buttonPin            = 12;
const int ledPin               = 13;

const char waitCode      = 'w';
const char errorCode     = 'x';
const char invalidCode   = 'i';

const char startCode     = 's';
const char endCode       = 'e';
const char revCode       = 'r';
const char fireCode      = 'f';
const char tiltCode      = 't';
const char panCode       = 'p';
const char velocityCode  = 'v';
const char heartbeatCode = 'h';
const char killCode      = 'k';

const int commandInputCount = 7;
char validInputs[commandInputCount] = {
    revCode, fireCode, tiltCode, panCode, velocityCode, heartbeatCode, killCode
};

const int startAutoFireCode = 65535;
const int stopAutoFireCode  = 0;

String s;
int i;

// PWM range 556-2420 => 1488
Servo panServo;
Servo tiltServo;

bool withinRange(int var, int low, int high) {
    return low <= var && var <= high;
}

/*
---------------------------------------------------------
                     Motion Control
*/

void tilt(int location) {
    if (withinRange(location, MAX_TILT_DOWN, MAX_TILT_UP)) {
        tiltServo.writeMicroseconds(location);
    }
}

void pan(int location) {
    if (withinRange(location, MAX_PAN_LEFT, MAX_PAN_RIGHT)) {
        panServo.writeMicroseconds(location);
    }
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
    delay(PUSHER_PULSE_ON_TIME);
    pusherOff();
    delay(PUSHER_PULSE_OFF_TIME);
}

void resetPusher() {
    pusherOff();
    while (digitalRead(pusherSwitchPin) == HIGH) pulsePusher();
}

/*
---------------------------------------------------------
                        Movement
*/

float panState       = PAN_MIDPOINT;
float panGoal        = PAN_MIDPOINT;
float panHalfway     = PAN_MIDPOINT;
float panVelocity    = 0.0;
float tiltState      = TILT_MIDPOINT;
float tiltGoal       = TILT_MIDPOINT;
float tiltHalfway    = TILT_MIDPOINT;
float tiltVelocity   = 0.0;
bool velocityMode = false;

long lastLocationUpdateTime = micros();
long timeElapsedSinceUpdate;

void setPanLocation(int argument) {
    // argument: [-700, 700]
    panHalfway = (panState + (PAN_MIDPOINT + argument)) / 2;
    panGoal = PAN_MIDPOINT + argument;
}

void setTiltLocation(int argument) {
    // argument: [-300, 500]
    tiltHalfway = (tiltState + (TILT_MIDPOINT + argument)) / 2;
    tiltGoal = TILT_MIDPOINT + argument;
}

/*
    Approximates velocity based on delta since last update, and
    updates pan state by velocity * delta.
*/
void incrementPanLocation(long delta) {
    bool movingRight = panHalfway < panGoal;
    bool halfwayDone = (movingRight && panState >= panHalfway) || (!movingRight && panState <= panHalfway);
    float scaled_delta = delta / 1000000.0;
    if (velocityMode) {
        panState += panVelocity * scaled_delta;
    } else {
        float increment = ACCELERATION * scaled_delta;
        if (!halfwayDone) {
            panVelocity += increment;
        } else {
            panVelocity -= increment;
            if (panVelocity < 0.1) {
                panVelocity = 0.1; 
            }
        }
        if (movingRight) {
            panState += panVelocity * scaled_delta;
        } else {
            panState -= panVelocity * scaled_delta;
        }
    }
    // If panState has elapsed panGoal, then set to panGoal
    if ((movingRight && panState >= panGoal) || (!movingRight && panState <= panGoal)) {
        panState = panGoal;
        panVelocity = 0.0;
    }
    pan((int) panState);
}

void incrementTiltLocation(long delta) {
    bool movingUp = tiltHalfway < tiltGoal;
    bool halfwayDone = (movingUp && tiltState >= tiltHalfway) || (!movingUp && tiltState <= tiltHalfway);
    float scaled_delta = delta / 1000000.0;
    if (velocityMode) {
        tiltState += tiltVelocity * scaled_delta;
    } else {
        float increment = ACCELERATION * scaled_delta;
        if (!halfwayDone) {
            tiltVelocity += increment;
        } else {
            tiltVelocity -= increment;
            if (tiltVelocity < 0.1) {
                tiltVelocity = 0.1;
            }
        }
        if (movingUp) {
            tiltState += tiltVelocity * scaled_delta;
        } else {
            tiltState -= tiltVelocity * scaled_delta;
        }
    }
    if ((movingUp && tiltState >= tiltGoal) || (!movingUp && tiltState <= tiltGoal)) {
        tiltState = tiltGoal;
        tiltVelocity = 0.0;
    }
    tilt((int) tiltState);
}

void updateLocation() {
    timeElapsedSinceUpdate = micros() - lastLocationUpdateTime;
    if (timeElapsedSinceUpdate > UPDATE_INTERVAL) {
        lastLocationUpdateTime = micros();
        if (panState != panGoal) {
            incrementPanLocation(timeElapsedSinceUpdate);
        }
        if (tiltState != tiltGoal) {
            incrementTiltLocation(timeElapsedSinceUpdate);
        }
    }
}

/*
---------------------------------------------------------
                         Firing
*/

int revSpeed = 0;
bool revving = false;
long lastRevUpdateTime = millis();

int remainingShots = 0;
bool pushing = false;
bool retracting = false;
long lastPushUpdateTime = millis();

// Power flywheels for 20ms, power down for up to 200ms
void updateFlywheels() {
    if (revSpeed == 0 || revSpeed == 255) return;
    int timeSinceLastRevUpdate = millis() - lastRevUpdateTime;
    if (revving && timeSinceLastRevUpdate > REV_UP_PERIOD) {
        revDown();
        revving = false;
        lastRevUpdateTime = millis();
    } else if (!revving && timeSinceLastRevUpdate > MAX_REV_DOWN_PERIOD * (1 - revSpeed / 255.0)) {
        revUp();
        revving = true;
        lastRevUpdateTime = millis();
    }
}

void updatePusher() {
    if (revSpeed < 10 || remainingShots == 0) return;
    int timeSinceLastPushUpdate = millis() - lastPushUpdateTime;
    if (!retracting && digitalRead(pusherSwitchPin) == HIGH) {
        retracting = true;
    } else if (retracting && digitalRead(pusherSwitchPin) == LOW) {
        retracting = false;
        remainingShots -= 1;
    }
    if (remainingShots == 0 || timeSinceLastPushUpdate > MAX_FIRE_TIME) {
            pusherOff();
            pushing = false;
            return;
        }
    if (pushing && timeSinceLastPushUpdate > PUSHER_PULSE_ON_TIME) {
        pusherOff();
        pushing = false;
        lastPushUpdateTime = millis();
    } else if (!pushing && timeSinceLastPushUpdate > PUSHER_PULSE_OFF_TIME) {
        pusherOn();
        pushing = true;
        lastPushUpdateTime = millis();
    }
}

// void fireShots(int numShots) {
//    startTime = millis();
//    revUp();
//    while (millis() - startTime < REV_UP_TIME);
//    for ( ; numShots > 0; numShots--) {
//        startTime = millis();
//        while (digitalRead(pusherSwitchPin) == LOW && millis() - startTime < MAX_FIRE_TIME) pulsePusher();
//        while (digitalRead(pusherSwitchPin) == HIGH && millis() - startTime < MAX_FIRE_TIME) pulsePusher();
//        if (millis() - startTime > MAX_FIRE_TIME) {
//            revDown();
//            reportError("Firing sensor not responding!");
//        }
//    }
//    revDown();
// }

// void fire(int argument) {
//    if (withinRange(argument, 1, 37)) {
//        fireShots(argument);
//    } else if (argument == 0) {
//        resetPusher();
//    } else if (argument == 65535) {
//        pusherOn();
//    } else {
//        reportError("Improper number of shots received!");
//    }
// }

/*
---------------------------------------------------------
                Serial Communication
*/

int serialAction;

void requestInput() {
    Serial.write(waitCode);
}

void reportInvalidInput(char message[]) {
    Serial.write(invalidCode);
    Serial.println(message);
}

bool isValidInput(char operationCode) {
    for (i = 0; i < commandInputCount; i++) {
        if (operationCode == validInputs[i]) return true;
    }
    return false;
}

byte getNextByte() {
    do {
        serialAction = Serial.read();
    } while (serialAction == -1);
    return byte(serialAction);
}

void processInput() {
    while (Serial.available() >= 5) {
        if (Serial.read() != startCode) {
            reportInvalidInput("Expected start byte");
            break;
        }
        char operationCode = Serial.read();
        if (!isValidInput(operationCode)) {
            reportInvalidInput("Invalid operation code");
            break;
        }

        byte byte0 = Serial.read();
        byte byte1 = Serial.read();

        if (Serial.read() != endCode) {
            reportInvalidInput("Expected end byte");
            break;
        }

        switch (operationCode) {
            case revCode:
                // [0, 255]
                revSpeed = byte0;
                // uint8_t timeout = byte1;
                if (revSpeed == 0) revDown();
                else if (revSpeed == 255) revUp();
                break;
            case fireCode:
                // [0, 255]
                remainingShots = byte0;
                lastPushUpdateTime = millis();
                // uint8_t shootingFrequency = byte1;
                break;
            case tiltCode:
                velocityMode = false;
                lastLocationUpdateTime = micros();
                setTiltLocation((byte0 << 8) + byte1);
                break;
            case panCode:
                velocityMode = false;
                lastLocationUpdateTime = micros();
                setPanLocation((byte0 << 8) + byte1);
                break;
            case velocityCode:
                velocityMode = true;
                lastLocationUpdateTime = micros();
                panVelocity = (int8_t) byte0 * VELOCITY_MULTIPLIER;
                tiltVelocity = (int8_t) byte1 * VELOCITY_MULTIPLIER;
                if (panVelocity < -0.0001) {
                    setPanLocation(MAX_PAN_LEFT - PAN_MIDPOINT);
                } else if (panVelocity > 0.0001) {
                    setPanLocation(MAX_PAN_RIGHT - PAN_MIDPOINT);
                }
                if (tiltVelocity < -0.0001) {
                    setTiltLocation(MAX_TILT_DOWN - TILT_MIDPOINT);
                } else if (tiltVelocity > 0.0001) {
                    setTiltLocation(MAX_TILT_UP - TILT_MIDPOINT);
                }
                break;
            case heartbeatCode:
                break;
            case killCode:
                break;
        }

        requestInput();
    }
}

/*
---------------------------------------------------------
*/

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
    requestInput();
}

void loop() {
    processInput();
    updateLocation();
    updateFlywheels();
    updatePusher();
}
