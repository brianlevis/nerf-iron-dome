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
#define PUSHER_PULSE_OFF_TIME 150

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
const char actionCode    = 'a';

const int commandInputCount = 8;
char validInputs[commandInputCount] = {
    revCode, fireCode, tiltCode, panCode, velocityCode, heartbeatCode, killCode, actionCode
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
                      Pin Control
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

void ledOn() {
    digitalWrite(ledPin, HIGH);
}

void ledOff() {
    digitalWrite(ledPin, LOW);
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
bool pusherMotorOn = false; // Is pusher motor on
bool retracting = false; // Is pusher motor retracting
long lastPushUpdateTime = millis();
long lastStateUpdateTime = millis();

// Power flywheels for 20ms, power down for up to 200ms
void updateFlywheels() {
    if (revSpeed == 0 || revSpeed == 255) return;
    long timeSinceLastRevUpdate = millis() - lastRevUpdateTime;
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
    if (revSpeed < 10 || remainingShots == 0) {
        remainingShots = 0;
        return;
    }
    long timeSinceLastPushUpdate = millis() - lastPushUpdateTime;
    bool updateState = (millis() - lastStateUpdateTime > 10);
    bool pusherOut = (digitalRead(pusherSwitchPin) == HIGH);
    if (!retracting && pusherOut && updateState) {
        retracting = true;
        lastStateUpdateTime = millis();
        ledOn();
    } else if (retracting && !pusherOut && updateState) {
        retracting = false;
        remainingShots -= 1;
        lastStateUpdateTime = millis();
        ledOff();
    }
    if (remainingShots == 0 || timeSinceLastPushUpdate > MAX_FIRE_TIME) {
            pusherOff();
            pusherMotorOn = false;
            return;
        }
    if (pusherMotorOn && timeSinceLastPushUpdate > PUSHER_PULSE_ON_TIME) {
        pusherOff();
        pusherMotorOn = false;
        lastPushUpdateTime = millis();
    } else if (!pusherMotorOn && timeSinceLastPushUpdate > PUSHER_PULSE_OFF_TIME) {
        pusherOn();
        pusherMotorOn = true;
        lastPushUpdateTime = millis();
    }
}

/*
---------------------------------------------------------
                  Action Sequences
*/

bool actionInProgress = false;
int actionNumber = 0;

void updateAction() {
    if (!actionInProgress) return;
    switch (actionNumber) {
        case 1:
            // lastLocationUpdateTime = micros();
            velocityMode = false;
            int clock = millis() % 30000;
            float t = 2 * 3.14 * clock / 30000.0;
            setPanLocation(600 * cos(t));
            setTiltLocation(100 + 200 * sin(t));
            break;
    }
}

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
            case actionCode:
                actionNumber = byte0;
                actionInProgress = (actionNumber != 0);
                break;
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
                actionInProgress = false;
                velocityMode = false;
                lastLocationUpdateTime = micros();
                setTiltLocation((byte0 << 8) + byte1);
                break;
            case panCode:
                actionInProgress = false;
                velocityMode = false;
                lastLocationUpdateTime = micros();
                setPanLocation((byte0 << 8) + byte1);
                break;
            case velocityCode:
                actionInProgress = false;
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
    updateAction();
}
