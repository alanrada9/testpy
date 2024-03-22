# Use the official Python runtime for ARMv7 as a base image
FROM arm32v7/python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Update package lists and install necessary system dependencies
RUN apt-get update && \
    apt-get install -y git build-essential python3-dev python3-pip python3-smbus i2c-tools

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip

# Install Flask and other required Python packages using pip
RUN pip3 install Flask adafruit-blinka adafruit-circuitpython-charlcd RPi.GPIO

# Clone Adafruit CircuitPython DHT library from GitHub
RUN git clone https://github.com/adafruit/Adafruit_CircuitPython_DHT.git

# Install Adafruit CircuitPython DHT library from the cloned repository
RUN cd Adafruit_CircuitPython_DHT && python3 setup.py install

# Move back to the working directory
WORKDIR /app

# Install RPi-LCD library using pip3
RUN pip3 install rpi-lcd

# Copy your Flask application code into the container
COPY . /app

# Expose the port Flask will be running on
EXPOSE 5000

# Set the container to run the Flask app when it starts
CMD ["python3", "app.py"]
