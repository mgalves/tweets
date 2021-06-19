#!/bin/sh

#
# author MIGUEL GALVES <mgalves@gmail.com>
# SCRIPT QUE EXECUTA O LEITOR DE DADOS DO TWEITTER.
#
wait=1

while true
do
    echo "RUNNING GRABBER"
    python3 grabber.py
    echo "GRABBER DOWN. SLEEPING..." $wait
    sleep $wait
    let wait=2*$wait
    if [ $wait -eq 1024 ]
    then
        echo "Waited too much....stopping"
        break
    fi
done