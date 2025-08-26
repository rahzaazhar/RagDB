# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install postgresql-client for pg_isready
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application's code to the working directory
COPY . .

# Copy the entrypoint script
COPY entrypoint.sh .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Make port 5000 available to the world outside this container
EXPOSE 8000

# Set the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

# Run app.py when the container launches
CMD ["python", "app.py"]
