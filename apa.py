#include <Servo.h>    // Library untuk mengendalikan servo motor.
#include <NewPing.h>  // Library untuk mengendalikan sensor ultrasonik NewPing.

// Pin-pins yang digunakan untuk mengendalikan motor L298N.
const int RightMotorForward = 7;
const int RightMotorBackward = 6;
const int LeftMotorForward = 5;
const int LeftMotorBackward = 4;

// Definisikan pin analog untuk setiap sensor inframerah
const int sensor1 = A0;
const int sensor2 = A1;
const int sensor3 = A2;
const int sensor4 = A3;
const int sensor5 = A4;

int nilaiSensor1 = analogRead(sensor1);
int nilaiSensor2 = analogRead(sensor2);
int nilaiSensor3 = analogRead(sensor3);
int nilaiSensor4 = analogRead(sensor4);
int nilaiSensor5 = analogRead(sensor5);

// Pin-pins yang digunakan untuk sensor ultrasonik.
#define trig_pin 9  // Pin trigger sensor ultrasonik (output).
#define echo_pin 10  // Pin echo sensor ultrasonik (input).

#define maximum_distance 200
// Variabel dan Objek Global pada program
boolean goesForward = false;  // Variabel untuk mengontrol arah pergerakan.
int distance = 100;           // Variabel jarak awal (initial distance).
int attempt = 0;


// Objek NewPing untuk mengukur jarak.
NewPing sonar(trig_pin, echo_pin, maximum_distance);

// Objek Servo untuk mengendalikan servo motor.
Servo servo_motor;

// Variabel yang digunakan dalam perulangan utama (loop).
int var = 1;

void setup() {
  pinMode(RightMotorForward, OUTPUT);
  pinMode(LeftMotorForward, OUTPUT);
  pinMode(LeftMotorBackward, OUTPUT);
  pinMode(RightMotorBackward, OUTPUT);

   // Set pin sensor sebagai input (ini sebenarnya default, tapi untuk kejelasan kita sebutkan)
  pinMode(sensor1, INPUT);
  pinMode(sensor2, INPUT);
  pinMode(sensor3, INPUT);
  pinMode(sensor4, INPUT);
  pinMode(sensor5, INPUT);

  // Menghubungkan objek servo_motor dengan pin 11.
  servo_motor.attach(13);
  servo_motor.write(90);  // Mengatur posisi awal servo motor ke 90 derajat.
  Serial.begin(9600);     // Inisialisasi komunikasi serial.
}

void loop() {
  kombinasi();
}

// Fungsi utama untuk kontrol gerakan dan penghindaran rintangan
void kombinasi() {
  int distanceRight = 0;
  int distanceLeft = 0;
  delay(50);

  Serial.println(nilaiSensor1);
  Serial.println(nilaiSensor2);
  Serial.println(nilaiSensor3);
  Serial.println(nilaiSensor4);
  Serial.println(nilaiSensor5);

  if (distance <= 40) {  // Jika jarak di depan kurang dari 40 cm
    moveStop();
    delay(300);
    distanceRight = lookRight();
    delay(300);
    Serial.println(distanceRight);
    distanceLeft = lookLeft();
    delay(300);
    Serial.println(distanceRight);
    lookForward();
    delay(300);
    moveBackward();
    delay(500);

    //Keputusan untuk belok berdasarkan jarak
    if (distanceRight >= distanceLeft) {
      moveStop();
      delay(300);
      turnRight();
      delay(100);
      
    } else {
      moveStop();
      delay(300);
      turnLeft();
      delay(100);
    }
    moveStop();  // Berhenti setelah berbelok
    delay(300);
  } else {
    moveForward();  // Lanjutkan bergerak maju jika tidak ada rintangan
    delay(300);
  }
  distance = readPing();  // Perbarui jarak
}

// Menggerakkan servo motor ke kanan untuk mengukur jarak
int lookRight() {
  servo_motor.write(0);
  delay(100);
  int distance = readPing();
  return distance;
}

// Menggerakkan servo motor ke kiri untuk mengukur jarak
int lookLeft() {
  servo_motor.write(180);
  delay(100);
  int distance = readPing();
  return distance;
}

int lookForward(){
  servo_motor.write(90);
  delay(50);
}

// Fungsi untuk membaca jarak menggunakan sensor ultrasonik
int readPing() {
  delay(70);
  int cm = sonar.ping_cm();
  if (cm == 0) {
    cm = 250;  // Set jarak ke maksimum jika tidak ada pengukuran
  }
  // Serial.print("Jarak: ");
  // Serial.print(cm);
  // Serial.println(" cm");

  return cm;
}

int readIR() {
  // Baca nilai dari setiap sensor
  int nilaiSensor1 = analogRead(sensor1);
  int nilaiSensor2 = analogRead(sensor2);
  int nilaiSensor3 = analogRead(sensor3);
  int nilaiSensor4 = analogRead(sensor4);
  int nilaiSensor5 = analogRead(sensor5);

  // Tampilkan nilai sensor di Serial Monitor
  Serial.print("Sensor 1: ");
  Serial.print(nilaiSensor1);
  Serial.print("\tSensor 2: ");
  Serial.print(nilaiSensor2);
  Serial.print("\tSensor 3: ");
  Serial.print(nilaiSensor3);
  Serial.print("\tSensor 4: ");
  Serial.print(nilaiSensor4);
  Serial.print("\tSensor 5: ");
  Serial.println(nilaiSensor5);
}

// Fungsi untuk menghentikan robot
void moveStop() {
  digitalWrite(RightMotorForward, LOW);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);
  digitalWrite(LeftMotorBackward, LOW);
}

// Fungsi untuk bergerak maju
void moveForward() {
  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorForward, HIGH);
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorBackward, LOW);
}

// Fungsi untuk bergerak maju
void moveBackward() {
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorForward, LOW);
  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);
}

// Fungsi untuk belok kanan
void turnLeft() {
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorForward, HIGH);
  delay(500);  // Durasi belok kanan
}

// Fungsi untuk belok kanan
void rotateLeft() {
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);
  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorForward, HIGH);
  delay(200);  // Durasi belok kanan
}

// Fungsi untuk belok kiri
void turnRight() {
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorForward, LOW);
  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorBackward, LOW);
  delay(200);  // Durasi belok kiri
}

// Fungsi untuk belok kanan
void rotateRight() {
  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorForward, LOW);
  delay(500);  // Durasi belok kanan
}
