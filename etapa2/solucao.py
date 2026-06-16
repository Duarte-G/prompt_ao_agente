"""
ETAPA 2 — SOLUÇÃO (ciclo completo de Tool Calling)
==================================================

Mostra o ciclo inteiro:
  1. Enviamos a pergunta + as ferramentas disponíveis.
  2. O modelo responde pedindo a ferramenta (stop_reason == "tool_use").
  3. Nosso código executa get_clima() e devolve o resultado como tool_result.
  4. O modelo lê o resultado e escreve a resposta final em linguagem natural.

Agora em modo chat: você pergunta no terminal e o histórico persiste entre
as perguntas, criando uma conversa contínua. Digite 'sair' para encerrar.

Uso:
    python solucao.py
"""

import os

import requests
from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

# Apenas uma sugestão exibida na tela — o usuário digita o que quiser.
EXEMPLO = "Como está o tempo em Maringá hoje?"


# --- A função real: consulta o clima de verdade no serviço gratuito wttr.in --
def get_clima(cidade: str) -> str:
    """Consulta a condição climática atual da cidade (serviço gratuito wttr.in).

    Não precisa de chave de API. Retorna algo como "Ensolarado, +25°C".
    """
    try:
        resp = requests.get(
            f"https://wttr.in/{cidade}",
            params={"format": "%C, %t", "lang": "pt", "m": ""},  # condição, temperatura (°C)
            headers={"User-Agent": "curl/8.0"},  # wttr.in devolve texto puro p/ clientes não-browser
            timeout=15,
        )
        resp.raise_for_status()
        texto = resp.text.strip()
        if not texto or "Unknown location" in texto or "Sorry" in texto:
            return f"Não foi possível obter o clima de '{cidade}'."
        return texto
    except requests.RequestException as e:
        return f"Erro ao consultar o clima: {e}"


# --- Schema da ferramenta: como o modelo "enxerga" a função get_clima --------
TOOLS = [
    {
        "name": "get_clima",
        "description": (
            "Retorna a condição climática atual de uma cidade. "
            "Use sempre que o usuário perguntar sobre o tempo, temperatura ou "
            "previsão de uma localidade específica."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cidade": {
                    "type": "string",
                    "description": "O nome da cidade, ex: 'Maringá'.",
                },
            },
            "required": ["cidade"],
        },
    }
]


def responder(client: anthropic.Anthropic, mensagens: list) -> None:
    """Roda o ciclo de tool calling para a última pergunta no histórico."""
    # PASSO 1 + 2: o modelo recebe a pergunta e decide usar a ferramenta.
    resposta = client.messages.create(
        model=MODELO,
        max_tokens=500,
        tools=TOOLS,
        messages=mensagens,
    )
    print(f"stop_reason: {resposta.stop_reason}")

    # PASSO 3: o modelo pediu uma ferramenta -> executamos e devolvemos.
    if resposta.stop_reason == "tool_use":
        # Localiza o bloco tool_use dentro do conteúdo da resposta.
        bloco_tool = next(b for b in resposta.content if b.type == "tool_use")

        nome = bloco_tool.name
        argumentos = bloco_tool.input
        print(f"O modelo pediu a ferramenta: {nome}({argumentos})")

        # Executa a função Python real correspondente.
        if nome == "get_clima":
            resultado = get_clima(argumentos["cidade"])
        else:
            resultado = f"Ferramenta desconhecida: {nome}"

        print(f"Resultado da função: {resultado}")

        # Guardamos a fala do modelo (o pedido da ferramenta) no histórico...
        mensagens.append({"role": "assistant", "content": resposta.content})
        # ...e devolvemos o resultado da ferramenta como uma mensagem do usuário.
        mensagens.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": bloco_tool.id,  # liga o resultado ao pedido
                        "content": resultado,
                    }
                ],
            }
        )

        # PASSO 4: o modelo lê o resultado e formula a resposta final.
        resposta_final = client.messages.create(
            model=MODELO,
            max_tokens=500,
            tools=TOOLS,
            messages=mensagens,
        )

        texto_final = next(
            b.text for b in resposta_final.content if b.type == "text"
        )
        print("-" * 40)
        print(f"Assistente: {texto_final}")
        # Guarda a resposta final para manter a conversa contínua.
        mensagens.append({"role": "assistant", "content": resposta_final.content})
    else:
        # O modelo respondeu direto, sem usar ferramenta.
        texto = next(b.text for b in resposta.content if b.type == "text")
        print(f"Assistente: {texto}")
        mensagens.append({"role": "assistant", "content": resposta.content})


def main() -> None:
    load_dotenv()
    client = anthropic.Anthropic()

    print("Assistente de clima — pergunte algo ('sair' para encerrar).")
    print(f"Ex.: {EXEMPLO}")

    # O histórico persiste entre as perguntas, criando uma conversa contínua.
    mensagens = []

    while True:
        pergunta = input("\nVocê: ").strip()
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("Até logo! 👋")
            break
        if not pergunta:
            continue

        mensagens.append({"role": "user", "content": pergunta})
        responder(client, mensagens)


if __name__ == "__main__":
    main()
