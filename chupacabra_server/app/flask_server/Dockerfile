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
ENV FLASK_APP=/app/chupacabra_server/app/flask_server.server
# TODO: Customize this
ENV FLASK_ENV=development

# Run the command
CMD [ \
    "python", "flask_server/server.py", \
    "--host=0.0.0.0", "--port=80", \
    "--grpc_host=chupacabra", "--grpc_port=80" \
]
