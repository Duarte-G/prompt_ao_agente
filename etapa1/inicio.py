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

Agora em modo chat: você digita perguntas no terminal até escrever 'sair'.

Uso:
    python inicio.py
"""

import os
import json

from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

# Apenas uma sugestão exibida na tela — o usuário digita o que quiser.
EXEMPLO = "Será que vai chover em Maringá amanhã? Quero saber se levo guarda-chuva."


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


def extrair(client: anthropic.Anthropic, pergunta: str) -> None:
    """Faz uma chamada ao modelo e imprime o JSON extraído da pergunta."""
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
        messages=[{"role": "user", "content": pergunta}],
    )

    texto = resposta.content[0].text
    print("Resposta crua do modelo:")
    print(texto)
    print("-" * 40)

    # Alguns modelos insistem em embrulhar o JSON em ```json ... ``` mesmo
    # quando o system prompt proíbe. Removemos a "cerca" antes de interpretar.
    texto_limpo = texto.strip()
    if texto_limpo.startswith("```"):
        texto_limpo = texto_limpo.split("```")[1]
        if texto_limpo.startswith("json"):
            texto_limpo = texto_limpo[len("json"):]
        texto_limpo = texto_limpo.strip()

    # Tenta interpretar como JSON para provar que o contrato foi cumprido.
    try:
        dados = json.loads(texto_limpo)
        print("JSON interpretado com sucesso:")
        print(f"  cidade        = {dados.get('cidade')}")
        print(f"  data_relativa = {dados.get('data_relativa')}")
        print(f"  intencao      = {dados.get('intencao')}")
    except json.JSONDecodeError:
        print("FALHOU: a resposta não é um JSON válido.")
        print("Revise seu system prompt (TODO a) e a temperature (TODO b).")


def main() -> None:
    load_dotenv()
    client = anthropic.Anthropic()

    print("Extrator de clima — digite uma pergunta ('sair' para encerrar).")
    print(f"Ex.: {EXEMPLO}")

    while True:
        pergunta = input("\nVocê: ").strip()
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("Até logo! 👋")
            break
        if not pergunta:
            continue

        extrair(client, pergunta)


if __name__ == "__main__":
    main()
