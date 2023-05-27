import asyncio
import datetime
import json
import logging
import os

import aio_pika

from resources.modules.email import Email
from resources.modules.log import Log


class RabbitMQ:
    """
    Classe responsável por consumir as mensagens da fila do RabbitMQ.
    """

    def __init__(self, worker, host, queues, username, password, port=5672, virtual_host="/", process_message_func=None):
        self.worker = worker
        self.host = host
        self.queues = queues
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.process_message_func = process_message_func
        self.last_email_time = None
        self.last_print_time = None

    async def callback(self, message):
        """
        Callback que será chamado quando uma mensagem for recebida da fila.

        Args:
            message (aio_pika.IncomingMessage): A mensagem recebida.
        """
        try:
            body = message.body
            data = json.loads(body.decode())
            logging.info(f"Mensagem recebida: {data}")
            
            print(f"[x] PROCESSANDO A MENSAGEM: ID {data['id']}, robo: {data['Robo']}")

            await self.process_message_func(self.worker, data)
            
            await message.ack()
        except Exception as e:
            logging.error(f"Erro ao processar a mensagem: %s", e)
            await message.ack()

    async def consume_messages_from_queue(self, queue):
        """
        Consumir as mensagens da fila.

        Args:
            queue (aio_pika.Queue): A fila a ser consumida.
        """
        async for message in queue:
            await self.consume_message(message)

    async def consume_message(self, message):
        """
        Consumir uma mensagem da fila.

        Args:
            message (aio_pika.IncomingMessage): A mensagem a ser consumida.
        """
        try:
            await self.process_logic(message)
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Erro ao consumir a mensagem: %s", e)
            await message.nack(requeue=True)

    async def process_logic(self, message):
        """
        Processar a lógica da mensagem.

        Args:
            message (aio_pika.IncomingMessage): A mensagem a ser processada.
        """
        try:
            body = message.body
            data = json.loads(body.decode())

            robo_name = data.get("Robo")
            if robo_name:
                await self.callback(message)
            else:
                logging.info("Mensagem devolvida para a fila - Robo não especificado.")
                await message.nack(requeue=True)
        except Exception as e:
            logging.error(f"Erro ao processar a lógica: %s", e)
            await message.nack(requeue=True)

    async def consume_queue(self):
        """
        Consumir a fila.
        """
        connection = None
        while True:
            try:
                connection = await aio_pika.connect_robust(
                    host=self.host,
                    port=self.port,
                    virtualhost=self.virtual_host,
                    login=self.username,
                    password=self.password
                )

                logging.info("Conectando ao RabbitMQ...")
                async with connection:
                    logging.info("[!] Conectado ao RabbitMQ!")
                    if self.last_print_time is None or (datetime.datetime.now() - self.last_print_time).total_seconds() > 3600:
                        print("[!] ------ Conectado ao RabbitMQ! ------ [!]")
                        self.last_print_time = datetime.datetime.now()
                        
                    channel = await connection.channel()
                    await channel.set_qos(prefetch_count=1)

                    tasks = []
                    for queue_name in self.queues:
                        queue_obj = await channel.declare_queue(queue_name, durable=True, arguments={'x-max-priority': 10})
                        task = asyncio.create_task(self.consume_messages_from_queue(queue_obj))
                        tasks.append(task)

                    await asyncio.gather(*tasks)
                    # Se a conexão for estabelecida e as mensagens forem consumidas com sucesso, sai do loop!
                    break 

            except aio_pika.exceptions.AMQPConnectionError as error:
                logging.error("[!] Erro ao tentar se conectar no RabbitMQ!")
                logging.error("Erro ao tentar se conectar no RabbitMQ! %s", error)
                
                # Verifica se já passou tempo suficiente desde o último e-mail enviado
                if self.last_email_time is None or (datetime.datetime.now() - self.last_email_time).total_seconds() > 3600:
                    Email().send_email_falha(worker=self.worker, mensagem="FALHA - CONEXÃO RABBITMQ!")
                    self.last_email_time = datetime.datetime.now()
                
                await asyncio.sleep(5)  # aguardar um pouco antes de tentar novamente