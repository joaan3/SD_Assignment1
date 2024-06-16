#!/bin/bash

# Verifica si se proporcionaron los argumentos requeridos
if [ $# -ne 3 ]; then
    echo "Uso: $0 <nombre> <ip> <puerto>"
    exit 1
fi

# Asigna los argumentos a variables
nombre=$1
ip=$2
puerto=$3

# Inicia un cliente con los parámetros proporcionados
/bin/python3 /home/milax/Baixades/SD_PRACTICA/SD_PRACTICA1/Client.py "$nombre" "$ip" "$puerto"