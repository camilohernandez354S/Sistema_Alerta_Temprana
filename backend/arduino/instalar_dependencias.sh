#!/bin/bash

echo "============================================================"
echo "Instalando dependencias para leer_serial.py"
echo "============================================================"
echo ""

echo "[1/3] Instalando pyserial..."
python3 -m pip install pyserial
if [ $? -ne 0 ]; then
    echo "Error instalando pyserial"
    exit 1
fi

echo ""
echo "[2/3] Instalando python-dotenv..."
python3 -m pip install python-dotenv
if [ $? -ne 0 ]; then
    echo "Error instalando python-dotenv"
    exit 1
fi

echo ""
echo "[3/3] Instalando requests..."
python3 -m pip install requests
if [ $? -ne 0 ]; then
    echo "Error instalando requests"
    exit 1
fi

echo ""
echo "============================================================"
echo "Dependencias instaladas correctamente!"
echo "============================================================"
echo ""
echo "Ahora puedes ejecutar:"
echo "  python3 leer_serial.py"
echo ""

