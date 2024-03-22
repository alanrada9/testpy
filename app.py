from flask import Flask, jsonify, abort
from rpi_lcd import LCD
import Adafruit_DHT
import time

app = Flask(__name__)

# Initialize LCD
lcd = LCD()

# Initialize DHT sensor (DHT22)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

def read_sensor_data():
    retries = 3  # Number of retries for sensor reading
    for _ in range(retries):
        try:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            return temperature, humidity
        except RuntimeError as e:
            print(f"Error reading DHT sensor: {e}")
            time.sleep(2)  # Wait before retrying
    raise RuntimeError("Unable to read sensor data after multiple retries")

def display_on_lcd(message):
    # Split the message into lines
    lines = message.split('\n')
    
    # Display each line on the LCD
    for i, line in enumerate(lines):
        lcd.text(line, i + 1)  # Adjust line number (1-indexed)

def read_light_status():
    # Placeholder function to simulate reading light status
    hour = time.localtime().tm_hour
    light_status = 'High' if 6 <= hour < 18 else 'Low'
    return light_status

@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        temperature, humidity = read_sensor_data()
        light_status = read_light_status()

        # Check if temperature and humidity are not None before formatting
        if temperature is not None and humidity is not None:
            data = {
                'temperature': temperature,
                'humidity': humidity,
                'light_status': light_status
            }
            # Format message for display on LCD
            display_message = f"Temp: {temperature:.1f}C\nHumidity: {humidity:.1f}%\nLight: {light_status}"
            display_on_lcd(display_message)
            return jsonify(data), 200
        else:
            return jsonify({'error': 'Unable to read sensor data'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Simulate health check failure for testing
        success = False  # Replace with actual health check logic
        
        if success:
            return jsonify({'status': 'alive'}), 200
        else:
            # Return 400 if health check is not successful
            abort(400, description='Health check failed')
    except Exception as e:
        print(f"Exception occurred during health check: {e}")
        abort(500)

if __name__ == '__main__':
    # Run the Flask app on host 0.0.0.0 and port 5000
    app.run(host='0.0.0.0', port=5002)

