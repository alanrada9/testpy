from flask import Flask, jsonify
from rpi_lcd import LCD
import Adafruit_DHT
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# Initialize LCD
lcd = LCD()

# Initialize DHT sensor (DHT22)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

# Initialize light sensor pin (adjust as needed)
LIGHT_SENSOR_PIN = 17

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)

def read_dht_sensor():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return humidity, temperature

def read_light_intensity():
    light_values = []
    for _ in range(10):  # Take multiple readings for accuracy
        light_values.append(GPIO.input(LIGHT_SENSOR_PIN))
        time.sleep(0.1)
    average_light_value = sum(light_values) / len(light_values)
    return average_light_value * 100  # Convert to percentage

def display_sensor_data(temperature, humidity, light_intensity):
    lcd.clear()
    lcd.text(f"Temp: {temperature:.1f}C", 1)
    lcd.text(f"Humidity: {humidity:.1f}%", 2)
    lcd.text(f"Light: {light_intensity:.2f}%", 3)

@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        humidity, temperature = read_dht_sensor()
        light_intensity = read_light_intensity()

        if humidity is not None and 0 <= humidity <= 100:
            temperature_str = f"{temperature:.2f}"
            humidity_str = f"{humidity:.2f}"
            light_intensity_str = f"{light_intensity:.2f}%"
            
            data = {
                'temperature': temperature_str,
                'humidity': humidity_str,
                'light_intensity': light_intensity_str
            }

            display_sensor_data(temperature, humidity, light_intensity)
            return jsonify(data), 200
        else:
            return jsonify({'error': 'Invalid humidity value'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        humidity, temperature = read_dht_sensor()
        light_intensity = read_light_intensity()

        if humidity is not None and temperature is not None:
            success = True
        else:
            success = False

        lcd.clear()
        if success:
            lcd.text("Status: OK", 1)
            return jsonify({'status': 'alive'}), 200
        else:
            lcd.text("Status: Failed", 1)
            return jsonify({'error': 'Health check failed'}), 400
    except Exception as e:
        print(f"Exception occurred during health check: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
