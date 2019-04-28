FROM python:3.6-stretch

# Add the code
ADD . /app

# Set the work directory
WORKDIR /app/chupacabra_server/app

# Install some required tools
RUN apt-get update && \
    apt-get -y install \
        build-essential \
        python3-dev \
        postgresql-client \
        make

# Install python requirements
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install -e /app/chupacabra_client

# Expose port 80
EXPOSE 80

# Set the pythonpath
ENV PYTHONPATH=/app/chupacabra_server/app

# Run the command
CMD [ \
    "python", "chupacabra_server/server.py", \
    "--host=0.0.0.0", "--port=80", \
    "--game-name=tic_tac_toe", "--game-server=tictactoe:80" \
]
