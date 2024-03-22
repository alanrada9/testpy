# Use an official Python runtime for ARMv7 as a base image
FROM arm32v7/python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && \
    apt-get install -y git build-essential python3-dev

# Clone the Adafruit CircuitPython CharLCD library from GitHub
RUN git clone https://github.com/adafruit/Adafruit_CircuitPython_CharLCD.git

# Copy the required files from the Adafruit_CircuitPython_CharLCD library
# Adjust the paths according to the library structure
COPY Adafruit_CircuitPython_CharLCD /usr/local/lib/python3.9/site-packages/Adafruit_CircuitPython_CharLCD

# Clone the Adafruit CircuitPython DHT library from GitHub
RUN git clone https://github.com/adafruit/Adafruit_CircuitPython_DHT.git

# Copy the required files from the Adafruit_CircuitPython_DHT library
# Adjust the paths according to the library structure
COPY Adafruit_CircuitPython_DHT /usr/local/lib/python3.9/site-packages/Adafruit_CircuitPython_DHT

# Install Flask and other required Python packages
RUN pip3 install Flask

# Copy your Flask application code into the container
COPY . /app

# Expose the port Flask will be running on
EXPOSE 5000

# Set the container to run the Flask app when it starts
CMD ["python3", "app.py"]
