# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME OpenExcept

# Run app.py when the container launches with multiple workers
CMD ["uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]