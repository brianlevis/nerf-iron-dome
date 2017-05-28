/* Initial Gun Test

  The circuit:
   Pusher switch on pin 4
   Acceleration motor relay input on pin 7
   Firing motor relay input on pin 8
   Manual input on pin 12

*/

#define REV_UP_TIME 750
#define AUTOMATIC false
#define SERIAL true
#define ENABLE true

const int pusherSwitchPin      =  4;
const int accelerationMotorPin =  7;
const int pusherMotorPin       =  8;
const int buttonPin            = 12;
const int ledPin               = 13;

unsigned long startTime;
int inByte;

void pusherOn() {
  if (ENABLE) digitalWrite(pusherMotorPin, LOW);
}

void pusherOff() {
  digitalWrite(pusherMotorPin, HIGH);
}

void waitForInput() {
  if (!SERIAL) while (digitalRead(buttonPin) == HIGH);
  else {
    do {
      inByte = Serial.read();
    } while (inByte != 'f');
    Serial.println("received f");
  }
}

void revUp() {
  if (ENABLE) digitalWrite(accelerationMotorPin, LOW);
}

void revDown() {
  digitalWrite(accelerationMotorPin, HIGH);
}

void fire() {
  if (!ENABLE) {
    digitalWrite(ledPin, HIGH);
    delay(1000);
    digitalWrite(ledPin, LOW);
    return;
  }
  if (AUTOMATIC) {
    pusherOn();
    delay(4000);
    pusherOff();
  }
  while (digitalRead(pusherSwitchPin) == LOW) pulsePusher();
  while (digitalRead(pusherSwitchPin) == HIGH) pulsePusher();
}

void pulsePusher() {
  pusherOn();
  delay(15);
  pusherOff();
  delay(80);
}

void setup() {
  Serial.begin(9600);
  pinMode(pusherSwitchPin, INPUT_PULLUP);
  pinMode(accelerationMotorPin, OUTPUT);
  pinMode(pusherMotorPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  revDown();
  pusherOff();
  waitForInput();
  while (digitalRead(pusherSwitchPin) == HIGH) pulsePusher();
}

void loop() {
  waitForInput();
  startTime = millis();
  revUp();
  while (millis() - startTime < REV_UP_TIME);
  fire();
  revDown();
}

