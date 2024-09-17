from datetime import datetime as dt

from app_schedule.send_email import send_email


def end_schedule():
    """Send email notifying end task"""
    time_ = dt.now().strftime("%d/%m/%Y %H:%M:%S")
    send_email("Tarefa encerrada", f"<p>Encerramento da tarefa em {time_}</p>")
