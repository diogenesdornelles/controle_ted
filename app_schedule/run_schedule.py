# from dataframe_handler import handler


import time

import schedule

from app_schedule.execute_pipeline import execute_pipeline


def run_schedule():
    """Função que executa a rotina no sistema"""

    # Executa imediatamente no primeiro loop
    execute_pipeline()

    # Agendar para rodar diariamente às 06:00
    schedule.every().day.at("06:00").do(execute_pipeline)

    while True:
        schedule.run_pending()  # Verifica as tarefas pendentes
        time.sleep(60)  # Verifica a cada 60 segundos
