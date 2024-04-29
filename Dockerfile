# Use the official Python image as a base
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# set PYTHONPATH
ENV PYTHONPATH /app/src

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code into the container
COPY . .

# Run the bot when the container launches
CMD ["python", "src/TalkTurbo/Turbo.py", "--no-user-identifiers", "--disable-image-storage"]
