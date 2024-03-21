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

# Light sensor pin (adjust as needed)
LIGHT_SENSOR_PIN = 17

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)  # Setup light sensor pin as input

def read_dht_sensor():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return humidity, temperature

def read_light_intensity():
    # Read light intensity from light sensor
    light_value = 0
    for _ in range(10):  # Take multiple readings for accuracy
        light_value += GPIO.input(LIGHT_SENSOR_PIN)
        time.sleep(0.1)
    average_light_value = light_value / 10  # Calculate average of readings
    return average_light_value

def display_sensor_data(temperature, humidity, light_intensity):
    # Clear LCD before displaying new data
    lcd.clear()

    # Display temperature on LCD
    lcd.text(f"Temp: {temperature:.1f}C", 1)
    
    # Display humidity on LCD
    lcd.text(f"Humidity: {humidity:.1f}%", 2)
    
    # Display light intensity on LCD
    lcd.text(f"Light: {light_intensity:.1f}%", 3)

@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        humidity, temperature = read_dht_sensor()
        light_intensity = read_light_intensity()

        # Check if humidity is within valid range (0-100)
        if humidity is not None and 0 <= humidity <= 100:
            # Convert temperature and humidity to string format with desired precision
            temperature_str = f"{temperature:.2f}"
            humidity_str = f"{humidity:.2f}"
            
            data = {
                'temperature': temperature_str,
                'humidity': humidity_str,
                'light_intensity': f"{light_intensity:.2f}%"  # Add light intensity in percentage
            }

            # Display results on the LCD
            display_sensor_data(temperature, humidity, light_intensity)

            return jsonify(data), 200
        else:
            return jsonify({'error': 'Invalid humidity value'}), 500
    except Exception as e:
        print(f"Exception 
