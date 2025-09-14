FROM mcr.microsoft.com/devcontainers/python
# Install the xz-utils package
RUN apt-get update && apt-get install -y xz-utils

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
