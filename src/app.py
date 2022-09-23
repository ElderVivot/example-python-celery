from dataclasses import dataclass
from celery import chain

from task import ocr_documento, validar_cpf_no_governo


@dataclass
class Pessoa:
    nome: str
    telefone: str
    documento: str


def cadastro(pessoa: Pessoa):
    # ocr_documento.delay(pessoa.documento)  # delay indica pra executar depois, pra entrar na fila

    chain(
        ocr_documento.s(pessoa.documento),
        validar_cpf_no_governo.s(),
        # enviar_email -> poderia ter uma nova de enviar email
    )()

    return 'Cadastro em avaliação, você recebera um email em breve'


p = Pessoa(
    'Elder',
    '999999999',
    '../images/documento_errado.png'
)
cadastro(p)
