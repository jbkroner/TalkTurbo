# Use the official Python image as a base
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# set PYTHONPATH
ENV PYTHONPATH /app/src

# Copy the rest of the code into the container
COPY . .

# Install the Python dependencies
RUN pip install --no-cache-dir .

# Run the bot when the container launches
CMD ["turbo", "--no-user-identifiers", "--disable-image-storage"]
