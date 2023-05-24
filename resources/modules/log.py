import locale
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path


class Log():
    def __init__(self):
        """
        Inicializa o objeto Log.
        
        Args:
            robo (str): O nome do robô.
        """
        self.path = os.getenv("LOG_PATH")
        self.data_atual = datetime.now().strftime("%d-%m-%Y")
        self.filename = self.data_atual +'.log'
        self.gerar_log()

    def gerar_log(self):
        """
        Gera o arquivo de log.
        """
        if self.path is not None:
            Path(self.path).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=self.path + self.filename, 
            filemode='w',
            encoding='utf-8',
            level=logging.INFO,
            format="{asctime} - {levelname} - {funcName}:{lineno} - {message}",
            datefmt="%d/%m/%Y %H:%M:%S",
            style='{'
        )

    def delete_log(self):
        """
        Deleta o arquivo de log.
        """
        os.remove(self.path + self.filename)