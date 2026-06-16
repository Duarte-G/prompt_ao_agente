"""
ETAPA 1 — SOLUÇÃO
=================

Versão completa e funcional. Usa APENAS o system prompt para forçar o modelo
a extrair dados de um texto desestruturado e devolver estritamente um JSON.

Sem ferramentas (tools): o modelo responde com o JSON em texto puro.

Agora em modo chat: você digita perguntas no terminal até escrever 'sair'.

Uso:
    python solucao.py
"""

import os
import json

from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

# Apenas uma sugestão exibida na tela — o usuário digita o que quiser.
EXEMPLO = "Será que vai chover em Maringá amanhã? Quero saber se levo guarda-chuva."


# O contrato é explícito: o modelo é um extrator e só pode devolver JSON puro.
SYSTEM_PROMPT = """Você é um extrator de dados especializado em pedidos de clima.

Sua única tarefa é ler a mensagem do usuário e devolver um objeto JSON com
exatamente estas três chaves:

  - "cidade": o nome da cidade mencionada (string).
  - "data_relativa": a referência temporal do pedido, normalizada em minúsculas
    e sem acento (ex: "hoje", "amanha", "fim de semana"). Se não houver, use "hoje".
  - "intencao": a intenção do usuário em snake_case (ex: "consultar_clima").

Regras obrigatórias:
  - Responda SOMENTE com o JSON válido.
  - NÃO inclua texto antes ou depois do JSON.
  - NÃO use blocos de código markdown (nada de ```json).
  - Se algum dado não existir na mensagem, use null como valor.
"""


def extrair(client: anthropic.Anthropic, pergunta: str) -> None:
    """Faz uma chamada ao modelo e imprime o JSON extraído da pergunta."""
    resposta = client.messages.create(
        model=MODELO,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        # temperature=0 -> saída determinística, essencial para extração de dados.
        temperature=0,
        messages=[{"role": "user", "content": pergunta}],
    )

    texto = resposta.content[0].text
    print("Resposta crua do modelo:")
    print(texto)
    print("-" * 40)

    # Mesmo proibido pelo system prompt, alguns modelos insistem em embrulhar o
    # JSON em uma "cerca" de código (```json ... ```). Removemos antes de ler.
    texto_limpo = texto.strip()
    if texto_limpo.startswith("```"):
        texto_limpo = texto_limpo.split("```")[1]
        if texto_limpo.startswith("json"):
            texto_limpo = texto_limpo[len("json"):]
        texto_limpo = texto_limpo.strip()

    try:
        dados = json.loads(texto_limpo)
        print("JSON interpretado com sucesso:")
        print(f"  cidade        = {dados.get('cidade')}")
        print(f"  data_relativa = {dados.get('data_relativa')}")
        print(f"  intencao      = {dados.get('intencao')}")
    except json.JSONDecodeError:
        print("FALHOU: a resposta não é um JSON válido.")


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
