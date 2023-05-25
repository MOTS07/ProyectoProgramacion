FROM python:3.11.3

#Se mueve de directorio a progsegura
WORKDIR /progsegura

#con env se establecen las variables de entorno 
# ENV nombre_variable valor
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#Instalacion de dependencias
COPY requirements.txt /progsegura/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#RUN pip install --no-cache-dir django
#RUN pip install --no-cache-dir mysqlclient
RUN apt-get update
RUN apt-get install -y ccrypt
RUN apt-get install -y mariadb-client

#Por medio de directorio
#RUN mkdir /code y despues de copia como en la siguiente lista
COPY /ProyectoProgramacion1/ /progsegura/

#Para volumenes
# RUN mkdir /code
# WORKDIR /code
# -v ./app:/code significa que es el uso de volumenes 
#docker run --rm -ti -v ./app:/code demo_segura bash
# -v permite hacerlo con volumenes
#Docker compose -- se pasan los comandos

EXPOSE 8000

CMD [ "./start.sh", "conf-cth.env.cpt"]

# CMD python -u manage.py runserver 0.0.0.0:8000

#Ejecutar el contenedor en background 
#docker run --name demo --rm -d -p 9999:8000 -v ./app/code demo_segura


##bitacoras 
#docker logs -f demo 
