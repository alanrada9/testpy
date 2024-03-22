# Use the official Python runtime for ARMv7 as a base image
FROM arm32v7/python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git build-essential python3-dev python3-smbus i2c-tools

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip

# Install Flask, Adafruit-Blinka, Adafruit-CircuitPython-DHT, RPi.GPIO, and RPi-LCD
RUN pip3 install Flask adafruit-blinka adafruit-circuitpython-dht RPi.GPIO rpi-lcd

# Copy your Flask application code into the container
COPY . /app

# Expose the port Flask will be running on
EXPOSE 5000

# Set the container to run the Flask app when it starts
CMD ["python3", "app.py"]
