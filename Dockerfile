FROM debian:latest

RUN apt-get update
RUN apt-get install -y git build-essential autoconf sudo wget python2.7 python-dev postgresql sqlite3 libssl-dev libffi-dev python-dev libpq-dev rabbitmq-server postgresql-contrib-9.4

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN /usr/bin/python2.7 get-pip.py

RUN pip install -I pip==8.1.1
RUN pip install setuptools
RUN pip install pip-tools
RUN pip install sphinx
RUN pip install alabaster

RUN mkdir /var/run/decaf
RUN mkdir /etc/decaf
RUN mkdir /var/lib/decaf
RUN mkdir /etc/rabbitmq

RUN git clone https://github.com/CN-UPB/OpenBarista.git /home/openbarista

RUN echo "[{rabbit, [{loopback_users, []}]}]." > /etc/rabbitmq/rabbitmq.config

RUN /etc/init.d/postgresql start
RUN /etc/init.d/rabbitmq-server start
RUN /home/openbarista/scripts/create_dirs.sh
RUN find /home/openbarista/ -name '*.cfg' -exec cp {} /etc/decaf \;

RUN cd /home/openbarista && /usr/bin/make install
# i have no idea why it doesn't build on the first run
RUN cd /home/openbarista/components/decaf-specification && /usr/bin/make install

EXPOSE 5672

ENTRYPOINT /home/openbarista/start.sh



