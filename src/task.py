from celery import Celery
from httpx import post, get
from base64 import standard_b64encode

# example with rabbitmq -> estudar mais pra criar vhosts que pelo que entendi seria como tenants
# app = Celery(
#     broker='amqp://guest:guest@localhost:5672/'
# )

#
app = Celery(
    broker='redis://localhost:6379/0'
)

# app.conf.broker_url = 'redis://localhost:6379/0'


@app.task
def olamundo():
    return 'hello world'


@app.task(
    bind=True,
    # default_retry_delay=3, # a cada 3 segundos tenta novamente
    max_retries=5,  # tenta no maximo 5 vezes
    retry_backoff=True,  # vai tentando novamente, até dar certo, no primeiro ele tenta depois de 1 seg, se não der,
                         # tenta depois de 2 seg, depois 4seg e assim por diante
    autoretry_for=(Exception,)  # pra quais tipos de erro que ele deve tentar novamente
)
def ocr_documento(self, documento):
    documento = open(documento, 'rb').read()  # o 'rb' é pra indicar que está abrindo como binário

    image = standard_b64encode(documento).decode('utf-8')

    data = {'image': image}

    response = post(
        'https://live-159-external.herokuapp.com/document-to-text-choice',
        json=data,
        timeout=None
    )
    if response.status_code == 200:
        return response.json()
    raise Exception('Error in route')


class CPFError(BaseException):
    ...


@app.task(
    bind=True,
    default_retry_delay=3,  # a cada 3 segundos tenta novamente
    max_retries=5,  # tenta no maximo 5 vezes
    autoretry_for=(CPFError,)
)
def validar_cpf_no_governo(self, cpf):
    if isinstance(cpf, dict):
        cpf = cpf['cpf']
    response = get(
        f'http://live-159-external.herokuapp.com/check-cpf?cpf={cpf}',
        timeout=None
    )
    # rdb.set_trace()
    if response.status_code == 200:
        return response.json()['cpf-status']
    raise CPFError('Erro no cpf!')
