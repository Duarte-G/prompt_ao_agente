"""
ETAPA 3 — SOLUÇÃO (loop ReAct robusto)
======================================

Implementa o agente autônomo que encadeia 3 ferramentas para resolver, por ex.:

    "Qual o clima no CEP 01310-100? Salve em previsao.txt"

O loop segue o padrão ReAct: chama o modelo, executa as ferramentas que ele
pedir, devolve os resultados e repete até o modelo dar a resposta final.

Agora em modo chat: você conversa com o agente no terminal e o histórico
persiste entre os pedidos — ele lembra do que já foi dito. Digite 'sair'
para encerrar.

Uso:
    python solucao.py
"""

import os

import requests
from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

# Apenas uma sugestão exibida na tela — o usuário digita o que quiser.
EXEMPLO = "Qual o clima no CEP 01310-100? Salve em previsao.txt"

# Trava de segurança: impede loop infinito caso algo dê errado.
MAX_ITERACOES = 10


# =============================================================================
# As 3 ferramentas reais do agente.
# =============================================================================
def buscar_cep(cep: str) -> str:
    """Descobre a cidade a partir de um CEP brasileiro, consultando o ViaCEP.

    Observação: em redes corporativas o HTTPS pode ser interceptado (proxy com
    certificado próprio), o que pode quebrar a chamada. Nesse caso devolvemos o
    erro como texto e o agente segue o fluxo normalmente.
    """
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    try:
        resp = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=10)
        resp.raise_for_status()
        dados = resp.json()
        if dados.get("erro"):
            return f"CEP {cep} não encontrado."
        return dados.get("localidade", "cidade desconhecida")
    except requests.RequestException as e:
        return f"Erro ao consultar o CEP: {e}"


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


def salvar_arquivo(nome_arquivo: str, conteudo: str) -> str:
    """Salva o conteúdo em um arquivo de texto."""
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Arquivo '{nome_arquivo}' salvo com sucesso."


FUNCOES = {
    "buscar_cep": buscar_cep,
    "get_clima": get_clima,
    "salvar_arquivo": salvar_arquivo,
}


# =============================================================================
# Os schemas que o modelo enxerga.
# =============================================================================
TOOLS = [
    {
        "name": "buscar_cep",
        "description": "Descobre a cidade a partir de um CEP brasileiro.",
        "input_schema": {
            "type": "object",
            "properties": {"cep": {"type": "string", "description": "O CEP, ex: '01310-100'."}},
            "required": ["cep"],
        },
    },
    {
        "name": "get_clima",
        "description": "Retorna a condição climática atual de uma cidade.",
        "input_schema": {
            "type": "object",
            "properties": {"cidade": {"type": "string", "description": "O nome da cidade."}},
            "required": ["cidade"],
        },
    },
    {
        "name": "salvar_arquivo",
        "description": "Salva um texto em um arquivo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nome_arquivo": {"type": "string", "description": "O nome do arquivo, ex: 'previsao.txt'."},
                "conteudo": {"type": "string", "description": "O texto a ser gravado."},
            },
            "required": ["nome_arquivo", "conteudo"],
        },
    },
]


def rodar_agente(client: anthropic.Anthropic, mensagens: list) -> None:
    """Executa o loop ReAct sobre o histórico até o agente dar a resposta final."""
    for iteracao in range(1, MAX_ITERACOES + 1):
        print(f"\n===== Iteração {iteracao} =====")

        # RACIOCÍNIO: o modelo decide o próximo passo com base no histórico.
        resposta = client.messages.create(
            model=MODELO,
            max_tokens=1024,
            tools=TOOLS,
            messages=mensagens,
        )

        # Se o modelo não quer mais ferramentas, ele concluiu a tarefa.
        if resposta.stop_reason != "tool_use":
            texto_final = next(
                (b.text for b in resposta.content if b.type == "text"),
                "(o agente terminou sem texto)",
            )
            # Guarda a resposta final no histórico para manter a conversa.
            mensagens.append({"role": "assistant", "content": resposta.content})
            print("\n----- RESPOSTA FINAL -----")
            print(texto_final)
            return

        # AÇÃO: registra a fala do modelo (que contém os pedidos de ferramenta).
        mensagens.append({"role": "assistant", "content": resposta.content})

        # Um único turno pode pedir várias ferramentas — tratamos todas.
        resultados_tool = []
        for bloco in resposta.content:
            if bloco.type != "tool_use":
                continue

            nome = bloco.name
            argumentos = bloco.input
            print(f"  -> Ação: {nome}({argumentos})")

            funcao = FUNCOES.get(nome)
            if funcao is None:
                resultado = f"Ferramenta desconhecida: {nome}"
            else:
                try:
                    resultado = funcao(**argumentos)
                except Exception as e:  # nunca derruba o loop por erro de ferramenta
                    resultado = f"Erro ao executar {nome}: {e}"

            print(f"     Observação: {resultado}")

            resultados_tool.append(
                {
                    "type": "tool_result",
                    "tool_use_id": bloco.id,  # liga o resultado ao pedido certo
                    "content": resultado,
                }
            )

        # OBSERVAÇÃO: devolvemos todos os resultados numa única mensagem do usuário.
        mensagens.append({"role": "user", "content": resultados_tool})

    print("\n[!] Limite de iterações atingido sem resposta final.")


def main() -> None:
    load_dotenv()
    client = anthropic.Anthropic()

    print("Agente ReAct — peça algo ('sair' para encerrar).")
    print(f"Ex.: {EXEMPLO}")

    # O histórico persiste entre os pedidos: o agente lembra da conversa.
    mensagens = []

    while True:
        pedido = input("\nVocê: ").strip()
        if pedido.lower() in {"sair", "exit", "quit"}:
            print("Até logo! 👋")
            break
        if not pedido:
            continue

        mensagens.append({"role": "user", "content": pedido})
        rodar_agente(client, mensagens)


if __name__ == "__main__":
    main()
