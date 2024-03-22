from flask import Flask, jsonify
from rpi_lcd import LCD
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import asyncio

app = Flask(__name__)

# Inicializa el LCD
lcd = LCD()

# Inicializa el sensor DHT (DHT22)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # Pin GPIO para el sensor DHT22

# Especifica el pin GPIO para el sensor de luz
LIGHT_SENSOR_PIN = 17  # Puedes ajustar este valor según la configuración de tu hardware

# Variables para almacenar los valores anteriores de temperatura, luz y tiempo
previous_temperature = None
previous_light_value = None
last_health_check = time.time()  # Tiempo de la última comprobación de salud

async def read_dht_sensor():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return humidity, temperature

async def read_light_intensity():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)
    light_values = []
    for _ in range(10):  # Toma múltiples lecturas para mayor precisión
        light_values.append(GPIO.input(LIGHT_SENSOR_PIN))
        time.sleep(0.1)
    average_light_value = sum(light_values) / len(light_values)
    return average_light_value * 100  # Convierte a porcentaje

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
            previous_temperature = temperature  # Actualizar la temperatura anterior
            return jsonify({'temperature_change': f"{temperature_change:.2f}"}), 200
        else:
            return jsonify({'error': 'Invalid humidity value or no previous temperature data available'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

async def health_check():
    global last_health_check
    try:
        current_time = time.time()  # Obtener el tiempo actual en segundos

        if current_time - last_health_check >= 300:  # Realizar la comprobación de salud cada 5 minutos
            # Aquí puedes agregar la lógica de la comprobación de salud
            last_health_check = current_time  # Actualizar el tiempo de la última comprobación de salud
            return {'status': 'alive'}, 200
        else:
            return {'status': 'alive'}, 200  # Si no es tiempo de comprobar, simplemente devuelve el estado vivo
    except Exception as e:
        print(f"Exception occurred during health check: {e}")
        return {'error': str(e)}, 500

@app.route('/health', methods=['GET'])
async def handle_health_check():
    result, status = await health_check()
    return jsonify(result), status

if __name__ == '__main__':
    asyncio.run(app.run(host='0.0.0.0', port=5000))
