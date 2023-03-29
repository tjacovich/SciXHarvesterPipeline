FROM python:3.8

WORKDIR /app

ENV UBUNTU_FRONTEND=noninteractive
USER root
RUN apt update && apt -y install software-properties-common gcc runit-run
RUN git clone https://github.com/edenhill/librdkafka
RUN cd librdkafka && ./configure && make && make install && ldconfig

RUN python -m pip install --upgrade wheel pip

COPY requirements.txt /app
RUN pip install --no-cache-dir -U -r requirements.txt

COPY dev-requirements.txt /app
RUN pip install --no-cache-dir -U -r dev-requirements.txt

COPY scripts/entrypoint.sh /app/entrypoint.sh
COPY scripts/migrate_db.py /app/migrate_db.py

COPY scripts/sv/ /etc/sv/
RUN ln -s /etc/sv/APP /etc/service/
RUN ln -s /etc/sv/API /etc/service/

RUN ln -s /etc/service /service
RUN useradd -ms /bin/bash ads

ENTRYPOINT [ "/app/scripts/entrypoint.sh" ]
