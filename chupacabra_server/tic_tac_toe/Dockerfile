FROM python:3.6-stretch

# Add the code
ADD . /app

# Set the work directory
WORKDIR /app/chupacabra_server

# Install some required tools
RUN apt-get update && \
    apt-get -y install \
        build-essential \
        python3-dev \
        postgresql-client \
        make

# Install python requirements
RUN pip install -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Set the pythonpath
ENV PYTHONPATH=/app:/app/chupacabra_server

# Run the command
CMD ["python", "tic_tac_toe/server.py", "--host=0.0.0.0", "--port=5000"]
