# Worker Rabbitmq

Este é um projeto que escuta uma fila RabbitMQ e executa tarefas automatizadas com base nas mensagens recebidas.

## Descrição

O projeto consiste em um gerenciador de robôs que executa tarefas automatizadas com base em mensagens recebidas de uma fila RabbitMQ. O Worker recebe as mensagens da fila, formata ela adequadamente, identifica qual robô que será executado, inicia o processo do robô correspondente e realiza o envio dos inputs que será utilizado no robô, usando websocket.

## Funcionalidades

- Recebe mensagens da fila RabbitMQ.
- Formata as mensagens recebidas e inicia o processo do robô correspondente.
- Envia mensagens para o robô por meio de um websocket.
- Trata erros e registra logs.
- Envia notificação por e-mail caso de falhe ao consumir a fila.

## Requisitos

Antes de executar o projeto, certifique-se de ter os seguintes requisitos atendidos:

- Python 3.7 ou superior
- Pacotes necessários (veja o arquivo requirements.txt)

## Configuração

1. Clone este repositório em sua máquina local.
2. Instale as dependências usando o comando `pip install -r requirements.txt`.
3. Configure as variáveis de ambiente no arquivo `.env` com as informações necessárias, como host do RabbitMQ, usuário, senha, etc.

## Uso

Execute o arquivo `main.py` para iniciar o gerenciador do robô. Certifique-se de que o ambiente esteja configurado corretamente antes de executar o projeto.

## Contribuição

Contribuições são bem-vindas! Se você quiser contribuir para este projeto, siga as etapas abaixo:

1. Faça um fork deste repositório.
2. Crie uma branch para a sua feature (`git checkout -b feature/sua-feature`).
3. Faça commit de suas alterações (`git commit -am 'Adicione sua feature'`).
4. Faça push para a branch (`git push origin feature/sua-feature`).
5. Abra um pull request para [este repositório](https://github.com/joaoauvs/worker-rabbitmq).

## Autores

- João Alves da Silva Neto