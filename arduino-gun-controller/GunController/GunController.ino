/* Initial Gun Test

  The circuit:
   Pusher switch on pin 4
   Acceleration motor relay input on pin 7
   Firing motor relay input on pin 8
   Manual input on pin 12

*/

#define REV_UP_TIME 800
#define AUTOMATIC true

const int pusherSwitchPin      =  4;
const int accelerationMotorPin =  7;
const int pusherMotorPin       =  8;
const int buttonPin            = 12;

unsigned long startTime;

void revUp() {
  digitalWrite(accelerationMotorPin, HIGH);
}

void revDown() {
  digitalWrite(accelerationMotorPin, LOW);
}

void fire() {
  if (AUTOMATIC) {
    digitalWrite(pusherMotorPin, HIGH);
    delay(4000);
    digitalWrite(pusherMotorPin, HIGH);
  }
  while (digitalRead(pusherSwitchPin) == LOW) pulsePusher();
  while (digitalRead(pusherSwitchPin) == HIGH) pulsePusher();
}

void pulsePusher() {
  digitalWrite(pusherMotorPin, HIGH);
  delay(15);
  digitalWrite(pusherMotorPin, LOW);
  delay(80);
}

void setup() {
  pinMode(pusherSwitchPin, INPUT_PULLUP);
  pinMode(accelerationMotorPin, OUTPUT);
  pinMode(pusherMotorPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  while (digitalRead(buttonPin) == HIGH);
  delay(1000);
  revDown();
  while (digitalRead(pusherSwitchPin) == HIGH) pulsePusher();
}

void loop() {
  while (digitalRead(buttonPin) == HIGH);
  startTime = millis();
  revUp();
  while (millis() - startTime < REV_UP_TIME);
  fire();
  revDown();
}

