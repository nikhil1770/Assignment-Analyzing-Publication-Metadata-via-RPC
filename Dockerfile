# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all your files into the container
COPY . /app

# Install all required libraries from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Run your assignment script when the container starts
CMD ["python", "MDS202522_Assignment.py"]

