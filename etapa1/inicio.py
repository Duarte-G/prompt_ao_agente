"""
ETAPA 1 — O poder do System Prompt (extração estruturada)
=========================================================

Objetivo: usar APENAS o system prompt para forçar o modelo a ler um texto
desestruturado do usuário e devolver ESTRITAMENTE um JSON com as chaves:

    - cidade         (str)  -> a cidade mencionada
    - data_relativa  (str)  -> ex: "hoje", "amanha", "fim de semana"
    - intencao       (str)  -> o que o usuário quer (ex: "consultar_clima")

Não usamos ferramentas (tools) aqui. O modelo responde com o JSON em texto puro.

>>> Sua missão (procure os blocos TODO abaixo):
      a) Escrever o system prompt que obriga a extração das 3 chaves.
      b) Ajustar o parâmetro 'temperature' para deixar a saída determinística.

Uso:
    python inicio.py
"""

import os
import json

from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

# Frase de exemplo, desestruturada, como um humano falaria.
PERGUNTA_USUARIO = "Será que vai chover em Maringá amanhã? Quero saber se levo guarda-chuva."


# =============================================================================
# TODO (a): Escreva o System Prompt.
#
# Ele deve INSTRUIR o modelo a:
#   - Atuar como um extrator de dados.
#   - Responder SOMENTE com um objeto JSON válido (nada de texto antes/depois,
#     nada de ```json ... ```).
#   - Extrair exatamente estas chaves: "cidade", "data_relativa", "intencao".
#
# Dica: seja explícito. Quanto mais claro o contrato, mais confiável a saída.
# =============================================================================
SYSTEM_PROMPT = ""  # <-- substitua por sua instrução


def main() -> None:
    load_dotenv()
    client = anthropic.Anthropic()

    resposta = client.messages.create(
        model=MODELO,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        # =====================================================================
        # TODO (b): Ajuste a 'temperature'.
        #
        # Para extração de dados queremos a saída mais determinística possível.
        # Qual valor garante isso? Descomente a linha abaixo e preencha.
        # =====================================================================
        # temperature=...,
        messages=[{"role": "user", "content": PERGUNTA_USUARIO}],
    )

    texto = resposta.content[0].text
    print("Resposta crua do modelo:")
    print(texto)
    print("-" * 40)

    # Tenta interpretar como JSON para provar que o contrato foi cumprido.
    try:
        dados = json.loads(texto)
        print("JSON interpretado com sucesso:")
        print(f"  cidade        = {dados.get('cidade')}")
        print(f"  data_relativa = {dados.get('data_relativa')}")
        print(f"  intencao      = {dados.get('intencao')}")
    except json.JSONDecodeError:
        print("FALHOU: a resposta não é um JSON válido.")
        print("Revise seu system prompt (TODO a) e a temperature (TODO b).")


if __name__ == "__main__":
    main()
