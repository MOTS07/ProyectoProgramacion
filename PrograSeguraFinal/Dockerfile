FROM python:3.11.3

#crea el directorio requerimientos
RUN mkdir /requerimientos

#copia el archivo requerimientos.txt
COPY ./requirements.txt /requerimientos
#Se cambir de directorio a requerimientos
WORKDIR /requerimientos

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#Directorio del codigo django
RUN mkdir /code
WORKDIR /code
RUN mkdir /start
COPY ./run.sh /start
RUN chmod +x /start/run.sh
#Agregar usuario NoROOT
RUN useradd limitado -s /bin/bash

#Define el usuario limitado
USER limitado


#Crea las variables de entorno en el contenedor
ENV MYSQL_ROOT_PASSWORD=""
ENV MYSQL_DATABASE=""
ENV BD_USER=""
ENV BD_HOST=""
ENV BD_PORT="3306"
ENV BD_NAME=""
ENV SECRET_KEY=""

##Inicia el servicio 
CMD /start/run.sh

