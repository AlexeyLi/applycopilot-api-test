# Base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV FLASK_APP=app/__init__.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application in local environment (Not needed for Heroku)
# CMD ["flask", "run"]
