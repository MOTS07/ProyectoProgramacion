FROM tsl0922/ttyd

RUN apt-get -y update \
    && apt-get install -y openssh-client \
    && apt-get -y clean

EXPOSE 7681
#EXPOSE 22

ENV USER=""
ENV PASS=""

COPY ./run.sh /
RUN chmod 700 /run.sh
RUN useradd -m -s /bin/bash limitado && chown -R limitado:limitado /home/limitado

CMD /run.sh

