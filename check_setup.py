"""
check_setup.py — Validação rápida do ambiente do workshop de Agentes.

O que este script faz:
  1. Carrega as variáveis de ambiente do arquivo .env
  2. Verifica se a ANTHROPIC_API_KEY existe
  3. Faz uma chamada minúscula ao modelo para validar a conexão com a API
  4. Imprime 'TUDO PRONTO!' se tudo estiver funcionando

Uso:
    python check_setup.py
"""

import os
import sys

from dotenv import load_dotenv
import anthropic

# Modelo leve e barato, ideal para um teste de conexão.
MODELO_TESTE = "claude-haiku-4-5"


def main() -> None:
    # 1. Carrega o .env para dentro das variáveis de ambiente.
    load_dotenv()

    # 2. Verifica se a chave existe.
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "sua-chave-aqui":
        print("ERRO: ANTHROPIC_API_KEY não encontrada.")
        print("      Crie um arquivo .env (copie de .env.example) e preencha sua chave.")
        sys.exit(1)

    # 3. Faz uma chamada minúscula apenas para validar a conexão.
    client = anthropic.Anthropic(api_key=api_key)

    try:
        client.messages.create(
            model=MODELO_TESTE,
            max_tokens=5,
            messages=[{"role": "user", "content": "ping"}],
        )
    except anthropic.AuthenticationError:
        print("ERRO: chave inválida. Verifique a ANTHROPIC_API_KEY no seu .env.")
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"ERRO ao conectar com a API da Anthropic: {e}")
        sys.exit(1)

    # 4. Sucesso!
    print("TUDO PRONTO!")


if __name__ == "__main__":
    main()
