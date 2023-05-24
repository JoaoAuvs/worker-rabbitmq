import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from fnmatch import fnmatch
from os import listdir
from os.path import basename, isfile, join


class Email():

    def __init__(self):
        self.emailRemetente = os.getenv("emailRemetente")
        self.emailPassword = os.getenv("emailPassword")
        self.emailDestinatario = os.getenv("emailDestinatario")
        self.dataAtual = (datetime.today().strftime('%d/%m/%Y'))

    def send_email_falha(self, worker, mensagem):
        logging.info("Chamando função para enviar e-mail...")
        msg = EmailMessage()
        corpo_email = f"""
        Bom dia,

        Segue o Log em anexo para análise.

        Att,

        """
        msg['Subject'] = worker + ": " + mensagem
        msg['From'] = self.emailRemetente
        msg['To'] = self.emailDestinatario
        msg.set_content(str(corpo_email))
        with smtplib.SMTP_SSL('smtp.hostinger.com', 465) as smtp:
                smtp.login(self.emailRemetente, self.emailPassword)            
                smtp.send_message(msg)
        logging.info("E-mail enviado com sucesso!")