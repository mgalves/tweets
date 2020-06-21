#!/bin/sh

#
# author MIGUEL GALVES <mgalves@gmail.com>
# SCRIPT QUE EXECUTA O WORKER CELERY.
# Parametros obtidos por environment:
# PROCESSOR_HOW_MANY_TASKS - Quantas tasks um worker ira executar antes de ser substituido. Evita processos zumbis.
# PROCESSOR_HOW_MANY_WORKERS - Define concorrencia, quantos workers irao rodar ao mesmo tempo
#

celery -A processor worker -l INFO -n 'worker@%h' --max-tasks-per-child ${PROCESSOR_HOW_MANY_TASKS} -c ${PROCESSOR_HOW_MANY_WORKERS}