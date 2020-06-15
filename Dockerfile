FROM python:3.7-slim
# Get some custom packages
RUN apt-get update && apt-get install -y build-essential make gcc python3-dev

#project id
ENV PROJECT_ID airtime-vm
ENV MPEASA_TOPIC mpesa-calls

#key for json auth production file
ENV TOKEN_ID auth-token
ENV TOKEN_VERSION 1

#key for rabbitmq credetials for africastalking
ENV SECRET_ID mpesa-consumer
ENV SECRET_VERSION 3

#url for mpesa api
ENV MPESA_API mpesa-api-fopkrom3ka-ez.a.run.app

## make a local directory
RUN mkdir /opt/airtime-web
#RUN mkdir /var/log

WORKDIR /opt/airtime-web

# now copy all the files in this directory to /code
ADD . ./

# pip install the local requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# start the app server
CMD python app.py