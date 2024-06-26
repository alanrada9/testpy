from flask import Flask, jsonify
import subprocess
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import uuid


app = Flask(__name__)

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

def get_pi_info():
    # Obtener información del sistema
    system_info = {
        'hostname': subprocess.check_output(['hostname']).strip().decode('utf-8'),
        'serial_number': subprocess.check_output(['cat', '/proc/cpuinfo']).strip().decode('utf-8').split('\n')[-1].split(':')[-1].strip()
    }

    # Obtener información específica de la Raspberry Pi
    try:
        pi_info = {
            'model': subprocess.check_output(['cat', '/sys/firmware/devicetree/base/model']).strip().decode('utf-8'),
            'revision': subprocess.check_output(['cat', '/proc/cpuinfo']).strip().decode('utf-8').split('\n')[8].split(':')[-1].strip(),
            'firmware_version': subprocess.check_output(['vcgencmd', 'version']).strip().decode('utf-8'),
            'mac_address': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        }

        # Obtener dispositivos conectados
        usb_devices, network_devices = get_connected_devices()
        pi_info['usb_devices'] = usb_devices
        pi_info['network_devices'] = network_devices

    except Exception as e:
        pi_info = {'error': str(e)}

    return system_info, pi_info


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

            return jsonify(data), 200
        else:
            return jsonify({'error': 'Invalid humidity value'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/temperature', methods=['GET'])
def get_temperature():
    try:
        humidity, temperature = read_dht_sensor()

        if temperature is not None:
            temperature_str = f"{temperature:.2f} Celsius"
            return jsonify({'temperature': temperature_str}), 200
        else:
            return jsonify({'error': 'Unable to read temperature data'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/humidity', methods=['GET'])
def get_humidity():
    try:
        humidity, temperature = read_dht_sensor()

        if humidity is not None and 0 <= humidity <= 100:
            humidity_str = f"{humidity:.2f}%"
            return jsonify({'humidity': humidity_str}), 200
        else:
            return jsonify({'error': 'Invalid humidity value'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/light_intensity', methods=['GET'])
def get_light_intensity():
    try:
        light_intensity = read_light_intensity()

        if light_intensity is not None:
            light_intensity_str = f"{light_intensity:.2f}%"
            return jsonify({'light_intensity': light_intensity_str}), 200
        else:
            return jsonify({'error': 'Unable to read light intensity data'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health_check', methods=['GET'])
def health_check():
    try:
        # Add your health check logic here
        # For example, check if sensors are responsive
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        print(f"Exception occurred during health check: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/pi-info', methods=['GET'])
def get_pi_info_route():
    try:
        system_info, pi_info = get_pi_info()

        if 'error' in pi_info:
            return jsonify({'error': pi_info['error']}), 500
        else:
            return jsonify({
                'system_info': system_info,
                'pi_info': pi_info
            }), 200
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
