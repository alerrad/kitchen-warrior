FROM python:3.10-alpine

# Define working directory
WORKDIR /bot

# Copy requirements to container
COPY requirements.txt .

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy all files to container
COPY . .

# Run bot
CMD python3 ./src/main.py