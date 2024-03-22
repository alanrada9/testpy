from flask import Flask, jsonify
from rpi_lcd import LCD
import Adafruit_DHT
from gpiozero import LightSensor
import time
import asyncio

app = Flask(__name__)

# Initialize LCD
lcd = LCD()

# Initialize DHT sensor (DHT22)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # GPIO pin for DHT22 sensor

# Specify GPIO pin for light sensor
LIGHT_SENSOR_PIN = 17  # Adjust this value according to your hardware setup

# Variables to store previous temperature, light, and time values
previous_temperature = None
previous_light_value = None
last_health_check = time.time()  # Time of last health check

async def read_dht_sensor():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return humidity, temperature

async def read_light_intensity():
    light_sensor = LightSensor(LIGHT_SENSOR_PIN)
    return light_sensor.value * 100  # Convert to percentage

def display_sensor_data(temperature, humidity, light_intensity):
    lcd.clear()
    lcd.text(f"Temp: {temperature:.1f}C", 1)
    lcd.text(f"Humidity: {humidity:.1f}%", 2)
    lcd.text(f"Light: {light_intensity:.2f}%", 3)

@app.route('/sensor_data', methods=['GET'])
async def get_sensor_data():
    global previous_temperature
    try:
        humidity, temperature = await read_dht_sensor()

        if humidity is not None and temperature is not None and 0 <= humidity <= 100:
            temperature_str = f"{temperature:.2f}"
            humidity_str = f"{humidity:.2f}"
            
            data = {
                'temperature': temperature_str,
                'humidity': humidity_str,
            }

            display_sensor_data(temperature, humidity, None)
            return jsonify(data), 200
        else:
            return jsonify({'error': 'Invalid humidity value. Humidity should be between 0 and 100'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/light_data', methods=['GET'])
async def get_light_data():
    global previous_light_value
    try:
        light_intensity = await read_light_intensity()

        if light_intensity is not None:
            light_intensity_str = f"{light_intensity:.2f}%"
            
            data = {
                'light_intensity': light_intensity_str,
            }

            display_sensor_data(None, None, light_intensity)
            return jsonify(data), 200
        else:
            return jsonify({'error': 'Light intensity not updated'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/temperature_variation', methods=['GET'])
async def get_temperature_variation():
    global previous_temperature
    try:
        humidity, temperature = await read_dht_sensor()
        if previous_temperature is not None and temperature is not None and 0 <= humidity <= 100:
            temperature_change = temperature - previous_temperature
            previous_temperature = temperature  # Update previous temperature
            return jsonify({'temperature_change': f"{temperature_change:.2f}"}), 200
        else:
            return jsonify({'error': 'Invalid humidity value or no previous temperature data available'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

async def health_check():
    global last_health_check
    try:
        current_time = time.time()

        if current_time - last_health_check >= 300:  # Perform health check every 5 minutes
            # Add health check logic here
            last_health_check = current_time  # Update time of last health check
            return {'status': 'alive'}, 200
        else:
            return {'status': 'alive'}, 200  # If it's not time to check, simply return alive status
    except Exception as e:
        print(f"Exception occurred during health check: {e}")
        return {'error': str(e)}, 500

@app.route('/health', methods=['GET'])
async def handle_health_check():
    result, status = await health_check()
    return jsonify(result), status

if __name__ == '__main__':
    asyncio.run(app.run(host='0.0.0.0', port=5000))
