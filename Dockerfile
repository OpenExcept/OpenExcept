# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy scripts first and set permissions
COPY scripts/wait-for-it.sh scripts/wait-for-it.sh
COPY scripts/start.sh scripts/start.sh
RUN chmod +x scripts/wait-for-it.sh scripts/start.sh

# Copy the rest of the application
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -e .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME OpenExcept

# Use the start script as the entrypoint
ENTRYPOINT ["scripts/wait-for-it.sh", "postgres:5432", "--", "scripts/start.sh"]