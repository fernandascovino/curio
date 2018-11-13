FROM python:3.6

# Set the working directory to /app
COPY . /app
WORKDIR /app


RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN apt-get install python-importlib
RUN apt-get update

# Expose a port 
EXPOSE  5001

# Run app.py when the container launches
CMD gunicorn -w 2 -b 0.0.0.0:5001 -t 100000 --max-requests 20 --reload app:server