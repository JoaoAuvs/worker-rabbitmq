import asyncio
import ctypes
import json
import logging
import os
import sys

import aio_pika
import websockets
from dotenv import load_dotenv

from rabbitmq import RabbitMQ
from resources.modules.email import Email
from resources.modules.log import Log


class RobotManager:
    
    WORKER = os.getenv("WORKER")

    def __init__(self):
        self.lock = asyncio.Lock()

    def format_message(self, worker, message):
        """
        Formata a mensagem para ser enviada para o robô.

        Args:
            worker (str): O nome do worker.
            message (dict): A mensagem recebida da fila.

        Returns:
            dict: A mensagem formatada.
        """
        if not isinstance(message, dict):
            message = json.loads(message)
        message["worker"] = worker
        return message

    def create_command(self, robo):
        """
        Cria o comando para iniciar o robô.

        Args:
            robo (str): O nome do robô.

        Returns:
            list: O comando para iniciar o robô.
        """
        robo_path = os.path.join('C:\\RPA', robo)
        comando = [
            os.path.join(robo_path, '.venv', 'Scripts', 'python.exe'),
            os.path.join(robo_path, 'main.py'),
        ]
        return comando

    async def send_websocket_message(self, message) -> None:
        """
        Envia uma mensagem para o robô através do websocket.

        Args:
            message (dict): A mensagem a ser enviada.
        """
        async with websockets.connect('ws://localhost:6010') as websocket:
            logging.info("ENVIANDO MENSAGEM PARA O ROBÔ: %s", message["Robo"])
            await websocket.send(json.dumps(message))
            logging.info("MENSAGEM ENVIADA COM SUCESSO PARA O ROBÔ: %s", message["Robo"])

    async def start_process(self, worker, message) -> asyncio.subprocess.Process:
        """
        Inicia o processo do robô.

        Args:
            worker (str): O nome do worker.
            message (dict): A mensagem recebida da fila.

        Returns:
            asyncio.subprocess.Process: O processo do robô.
        """
        message = self.format_message(worker, message)
        robo = message["Robo"]
        comando = self.create_command(robo)
        
        async with self.lock:
            proc = await asyncio.create_subprocess_shell(
                ' '.join(comando),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                shell=True,
            )

            logging.info("ROBÔ INICIADO: %s", message["Robo"])

            if len(message) > 1:
                await asyncio.sleep(10)
                try:
                    await self.send_websocket_message(message)
                except Exception as e:
                    logging.error(f"Erro ao enviar mensagem para o robô: {e}")
                    if proc and proc.returncode is None:
                        proc.kill()
                        logging.info("ROBÔ FINALIZADO: %s", message["Robo"])
                                      
        stdout, stderr = await proc.communicate()

if __name__ == "__main__":
    log = Log()
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)
    load_dotenv()
    robot_manager = RobotManager()
    rabbitmq = RabbitMQ(
        worker=RobotManager.WORKER,
        host=os.getenv("RABBITMQ_HOST"),
        queues=[queue.strip().replace("'", "") for queue in os.getenv("QUEUES").split(',')],
        username=os.getenv("RABBITMQ_USER"),
        password=os.getenv("RABBITMQ_PASS"),
        process_message_func=robot_manager.start_process
    )
    try:
        asyncio.run(rabbitmq.consume_queue())
    except Exception as e:
        logging.error(f"Erro ao consumir a fila: {e}")
        Email().send_email_falha(worker=RobotManager.WORKER, mensagem="API [FALHA] - Falha ao consumir a Fila!")