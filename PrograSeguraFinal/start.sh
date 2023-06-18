#!/usr/bin/env bash

test $# -eq 1 || { echo 'Se esperaba sólo un parámetro'; exit 1; }

test -f "$1" || { echo 'Se esperaba un archivo env'; exit 1; }

archivo_env="$1"

for linea in $(ccdecrypt -c "$archivo_env"); do
    export "${linea}";
done

docker-compose up -d 
