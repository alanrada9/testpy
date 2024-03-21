# Use the official Python runtime for ARMv7 as a base image
FROM arm32v7/python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies if needed (optional, depending on your application's requirements)
RUN apt-get update && \
    apt-get install -y git build-essential python3-dev python3-pip python3-smbus i2c-tools

# Install Flask and other required Python packages
RUN pip3 install Flask adafruit-blinka adafruit-circuitpython-dht adafruit-circuitpython-charlcd

# Install Adafruit_Python_DHT and RPi-LCD library dependencies
RUN apt-get install -y python3-smbus i2c-tools

# Install Adafruit_Python_DHT and RPi-LCD library using pip3
RUN pip3 install Adafruit_Python_DHT rpi-lcd

# Copy your Flask application code into the container
COPY . /app

# Expose the port Flask will be running on
EXPOSE 5000

# Set the container to run the Flask app when it starts
CMD ["python3", "app.py"]
