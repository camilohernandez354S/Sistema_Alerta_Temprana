import serial
import time

# Cambia el puerto según tu sistema (ejemplo: 'COM3' en Windows, '/dev/ttyACM0' en Linux)
PUERTO = 'COM5'
BAUDIOS = 9600

def main():
    try:
        arduino = serial.Serial(PUERTO, BAUDIOS, timeout=1)
        print(f"Conectado a {PUERTO} a {BAUDIOS} baudios.")
        time.sleep(2)  # Espera a que el Arduino reinicie

        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8', errors='ignore').strip()
                print(f"Dato recibido: {linea}")
            time.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
