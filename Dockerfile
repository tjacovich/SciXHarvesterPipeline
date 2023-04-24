FROM python:3.8

WORKDIR /app

ENV UBUNTU_FRONTEND=noninteractive
USER root
RUN apt update && apt -y install software-properties-common gcc runit-run
RUN git clone https://github.com/edenhill/librdkafka
RUN cd librdkafka && ./configure && make && make install && ldconfig

RUN python -m pip install --upgrade wheel pip
COPY SciXHarvester /app/SciXHarvester
COPY README.md /app/README.md 
COPY pyproject.toml /app
RUN pip install .
#RUN pip install --no-cache-dir -U -r requirements.txt

#COPY dev-requirements.txt /app
#RUN pip install --no-cache-dir -U -r dev-requirements.txt

COPY SciXHarvester/scripts/entrypoint.sh /app/entrypoint.sh
COPY SciXHarvester/scripts/migrate_db.py /app/migrate_db.py

COPY SciXHarvester/scripts/sv/ /etc/sv/
RUN ln -s /etc/sv/APP /etc/service/
RUN ln -s /etc/sv/API /etc/service/

RUN ln -s /etc/service /service
RUN useradd -ms /bin/bash ads

WORKDIR /app/SciXHarvester

ENTRYPOINT [ "/app/SciXharvester/scripts/entrypoint.sh" ]
