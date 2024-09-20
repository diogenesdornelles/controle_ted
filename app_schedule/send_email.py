import email.message
import smtplib
import traceback

from settings import settings


def send_email(subject: str, body: str) -> bool:
    """Envia email

    Args:
        subject (str): assunto
        body (str): corpo do email

    Returns:
        bool: true se houve êxito
    """
    try:
        sender = "gptdornelles@gmail.com"
        to = "diogenes.dornelles@gmail.com"
        msg = email.message.Message()
        msg["Subject"] = f"TED {subject}: Aviso de prazo!"
        msg["From"] = sender
        msg["To"] = to
        pwd = settings.gmail_pwd
        msg.add_header("Content-Type", "text/html")
        msg.set_payload(body)

        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(msg["From"], pwd)
        s.sendmail(msg["From"], msg["To"], msg.as_string().encode("utf-8"))
        s.quit()  # Fechar a conexão SMTP
        return True
    except Exception as err:
        print("Erro ao enviar email:")
        print(err)
        traceback.print_exc()  # Para exibir o rastreamento do erro completo
        return False


if __name__ == "__main__":
    send_email("aviso", "<p>Ola mundo</p>:")
