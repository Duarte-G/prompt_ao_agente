"""
ETAPA 2 — Tool Calling (conectando o modelo ao mundo real)
==========================================================

Na Etapa 1 o modelo apenas EXTRAIU a intenção. Agora vamos EXECUTAR uma ação:
ligar o pedido do usuário a uma função Python real de clima.

O fluxo do Tool Calling tem 4 passos:
  1. Enviamos a pergunta + a descrição das ferramentas disponíveis.
  2. O modelo decide usar uma ferramenta -> responde com stop_reason == "tool_use".
  3. NOSSO código executa a função e devolve o resultado ao modelo.
  4. O modelo lê o resultado e formula a resposta final em linguagem natural.

>>> Sua missão (procure os blocos TODO):
      a) Escrever o schema JSON da ferramenta get_clima.
      b) Tratar o stop_reason == "tool_use": capturar os argumentos e executar
         a função get_clima().

Uso:
    python inicio.py
"""

import os

from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

PERGUNTA_USUARIO = "Como está o tempo em Maringá hoje?"


# --- A "função real" (mockada para o workshop) -------------------------------
def get_clima(cidade: str) -> str:
    """Simula a consulta a uma API de clima."""
    return "25 graus e ensolarado"


# =============================================================================
# TODO (a): Descreva a ferramenta para o modelo.
#
# O schema precisa de:
#   - "name": o nome da função que o modelo vai "chamar" (ex: "get_clima").
#   - "description": explique o que ela faz. O modelo usa isso para decidir
#     QUANDO chamar a ferramenta — seja claro.
#   - "input_schema": um JSON Schema com a propriedade "cidade" (string) e
#     a lista "required".
#
# Modelo de referência:
#   {
#       "name": "...",
#       "description": "...",
#       "input_schema": {
#           "type": "object",
#           "properties": { "cidade": {"type": "string", "description": "..."} },
#           "required": ["cidade"],
#       },
#   }
# =============================================================================
TOOLS = [
    # <-- escreva o schema da ferramenta aqui
]


def main() -> None:
    load_dotenv()
    client = anthropic.Anthropic()

    mensagens = [{"role": "user", "content": PERGUNTA_USUARIO}]

    # PASSO 1 + 2: enviamos a pergunta e o modelo decide se usa a ferramenta.
    resposta = client.messages.create(
        model=MODELO,
        max_tokens=500,
        tools=TOOLS,
        messages=mensagens,
    )

    print(f"stop_reason: {resposta.stop_reason}")

    # =========================================================================
    # TODO (b): Trate o caso em que o modelo pediu uma ferramenta.
    #
    # Quando resposta.stop_reason == "tool_use":
    #   1. Encontre o bloco de conteúdo cujo .type == "tool_use".
    #   2. Leia os argumentos em bloco.input  (ex: bloco.input["cidade"]).
    #   3. Execute get_clima(cidade) e guarde o resultado.
    #   4. Imprima qual ferramenta o modelo pediu e com quais argumentos.
    #
    # (No PASSO 3/4 completo, devolveríamos esse resultado ao modelo — veja
    #  solucao.py. Aqui, basta executar a função e mostrar o resultado.)
    # =========================================================================
    if False:  # <-- troque pela condição correta
        pass


if __name__ == "__main__":
    main()
