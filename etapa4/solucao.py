"""
ETAPA 4 — SOLUÇÃO (níveis Intermediário + Avançado)
===================================================

Estende o agente da Etapa 3 com novas ferramentas, SEM tocar no loop ReAct:

  [INTERMEDIÁRIO]  agendar_evento(titulo, data) -> grava em 'agenda.csv'
  [AVANÇADO]       lembrar_fato / consultar_memoria -> persistem em 'memoria.json'

Repare: adicionar capacidades = escrever a função + registrar em FUNCOES +
descrever em TOOLS. O motor do agente permanece intacto e genérico.

Uso:
    python solucao.py
"""

import os
import csv
import json

import requests
from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

# Pedido que exercita as ferramentas novas de uma vez só.
PEDIDO = (
    "Agende a 'Reunião de Equipe' para 2025-07-01 e guarde na memória que o "
    "responsável pelo projeto é o Gabriel. Depois me diga quem é o responsável."
)

MAX_ITERACOES = 10

ARQUIVO_AGENDA = "agenda.csv"
ARQUIVO_MEMORIA = "memoria.json"


# =============================================================================
# Ferramentas originais (Etapa 3).
# =============================================================================
def buscar_cep(cep: str) -> str:
    """Consulta o CEP na API gratuita do ViaCEP e retorna a cidade."""
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    try:
        resp = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=10)
        dados = resp.json()
        if dados.get("erro"):
            return f"CEP {cep} não encontrado."
        return dados.get("localidade", "cidade desconhecida")
    except requests.RequestException as e:
        return f"Erro ao consultar o CEP: {e}"


def get_clima(cidade: str) -> str:
    """Simula a consulta a uma API de clima."""
    return "25 graus e ensolarado"


def salvar_arquivo(nome_arquivo: str, conteudo: str) -> str:
    """Salva o conteúdo em um arquivo de texto."""
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Arquivo '{nome_arquivo}' salvo com sucesso."


# =============================================================================
# [INTERMEDIÁRIO] Agenda em CSV.
# =============================================================================
def agendar_evento(titulo: str, data: str) -> str:
    """Adiciona um evento ao arquivo agenda.csv (cria o cabeçalho se necessário)."""
    arquivo_novo = not os.path.exists(ARQUIVO_AGENDA)
    with open(ARQUIVO_AGENDA, "a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        if arquivo_novo:
            escritor.writerow(["titulo", "data"])  # cabeçalho
        escritor.writerow([titulo, data])
    return f"Evento '{titulo}' agendado para {data} em {ARQUIVO_AGENDA}."


# =============================================================================
# [AVANÇADO] Memória local persistente em JSON.
# =============================================================================
def _carregar_memoria() -> dict:
    """Lê o memoria.json; devolve dict vazio se não existir ou estiver corrompido."""
    if not os.path.exists(ARQUIVO_MEMORIA):
        return {}
    try:
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def lembrar_fato(chave: str, valor: str) -> str:
    """Salva um fato (par chave-valor) na memória persistente."""
    memoria = _carregar_memoria()
    memoria[chave] = valor
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)
    return f"Memorizado: {chave} = {valor}."


def consultar_memoria(chave: str) -> str:
    """Recupera um fato da memória pela chave."""
    memoria = _carregar_memoria()
    if chave in memoria:
        return f"{chave} = {memoria[chave]}"
    return f"Não há nada memorizado sobre '{chave}'."


FUNCOES = {
    "buscar_cep": buscar_cep,
    "get_clima": get_clima,
    "salvar_arquivo": salvar_arquivo,
    "agendar_evento": agendar_evento,
    "lembrar_fato": lembrar_fato,
    "consultar_memoria": consultar_memoria,
}


# =============================================================================
# Schemas (incluindo as ferramentas novas).
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
    {
        "name": "agendar_evento",
        "description": "Agenda um evento, salvando-o em uma planilha (agenda.csv).",
        "input_schema": {
            "type": "object",
            "properties": {
                "titulo": {"type": "string", "description": "O título do evento."},
                "data": {"type": "string", "description": "A data do evento, ex: '2025-07-01'."},
            },
            "required": ["titulo", "data"],
        },
    },
    {
        "name": "lembrar_fato",
        "description": (
            "Memoriza um fato para lembrar depois. Use quando o usuário pedir "
            "para você 'lembrar', 'anotar' ou 'guardar' uma informação."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chave": {"type": "string", "description": "O assunto do fato, ex: 'responsavel_projeto'."},
                "valor": {"type": "string", "description": "O conteúdo a memorizar, ex: 'Gabriel'."},
            },
            "required": ["chave", "valor"],
        },
    },
    {
        "name": "consultar_memoria",
        "description": (
            "Consulta um fato memorizado anteriormente. Use quando o usuário "
            "perguntar algo que você pode ter anotado antes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chave": {"type": "string", "description": "O assunto a consultar, ex: 'responsavel_projeto'."},
            },
            "required": ["chave"],
        },
    },
]


def main() -> None:
    load_dotenv()
    client = anthropic.Anthropic()

    mensagens = [{"role": "user", "content": PEDIDO}]

    for iteracao in range(1, MAX_ITERACOES + 1):
        print(f"\n===== Iteração {iteracao} =====")

        resposta = client.messages.create(
            model=MODELO,
            max_tokens=1024,
            tools=TOOLS,
            messages=mensagens,
        )

        if resposta.stop_reason != "tool_use":
            texto_final = next(
                (b.text for b in resposta.content if b.type == "text"),
                "(o agente terminou sem texto)",
            )
            print("\n----- RESPOSTA FINAL -----")
            print(texto_final)
            return

        mensagens.append({"role": "assistant", "content": resposta.content})

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
                except Exception as e:
                    resultado = f"Erro ao executar {nome}: {e}"

            print(f"     Observação: {resultado}")

            resultados_tool.append(
                {
                    "type": "tool_result",
                    "tool_use_id": bloco.id,
                    "content": resultado,
                }
            )

        mensagens.append({"role": "user", "content": resultados_tool})

    print("\n[!] Limite de iterações atingido sem resposta final.")


if __name__ == "__main__":
    main()
