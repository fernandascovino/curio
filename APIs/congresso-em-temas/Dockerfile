FROM python:3.6

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

# Set the working directory to /app
COPY . /api
WORKDIR /api

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Expose a port
EXPOSE  5006

# Run app.py when the container launches
CMD gunicorn -w 2 -b 0.0.0.0:5006 -t 100000 --max-requests 20 --reload api:app
