# Use an official Python runtime as a parent image
FROM python:3.9-slim


# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Update and install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    libhdf5-dev \
    libblas-dev \
    liblapack-dev \
    gfortran \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Upgrade pip
RUN pip install --upgrade pip

# Install packages step by step to debug
RUN pip install --no-cache-dir Flask
RUN pip install --no-cache-dir tensorflow==2.10.0
RUN pip install --no-cache-dir numpy==1.26.0
RUN pip install --no-cache-dir Pillow
RUN pip install --no-cache-dir pymongo
RUN pip install --no-cache-dir aiobotocore
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir flask_bcrypt

RUN pip install --no-cache-dir h5py



# Expose the port the app runs on
EXPOSE 5001

# Command to run the application
CMD ["python", "app.py"]
