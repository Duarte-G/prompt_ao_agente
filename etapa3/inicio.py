"""
ETAPA 3 — O Loop ReAct (o agente autônomo)
==========================================

Até agora o modelo usou UMA ferramenta, UMA vez. Agora ele recebe um pedido
complexo e precisa encadear VÁRIAS ferramentas sozinho, sem intervenção humana:

    "Qual o clima no CEP 01310-100? Salve em previsao.txt"

Para resolver, o agente precisa, em sequência:
    1. buscar_cep("01310-100")   -> descobrir a cidade
    2. get_clima(cidade)          -> consultar o clima
    3. salvar_arquivo(...)        -> gravar o resultado
    4. responder ao usuário em texto

Isso é o padrão ReAct (Reasoning + Acting): o modelo RACIOCINA sobre o próximo
passo, AGE chamando uma ferramenta, OBSERVA o resultado e repete — até concluir.

>>> Sua missão: escrever o LOOP do agente (o grande TODO lá embaixo).

Uso:
    python inicio.py
"""

import os

import requests
from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

PEDIDO = "Qual o clima no CEP 01310-100? Salve em previsao.txt"


# =============================================================================
# As 3 ferramentas reais do agente (já prontas).
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


# Mapa nome-da-ferramenta -> função Python, usado para despachar a execução.
FUNCOES = {
    "buscar_cep": buscar_cep,
    "get_clima": get_clima,
    "salvar_arquivo": salvar_arquivo,
}


# =============================================================================
# Os schemas que o modelo enxerga (já prontos).
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


def main() -> None:
    load_dotenv()
    client = anthropic.Anthropic()

    # O histórico começa só com o pedido do usuário.
    mensagens = [{"role": "user", "content": PEDIDO}]

    # =========================================================================
    # TODO (o coração desta etapa): escreva o LOOP do agente.
    #
    # while True:
    #   1. Chame a API: client.messages.create(model=MODELO, max_tokens=1024,
    #      tools=TOOLS, messages=mensagens).
    #
    #   2. SE resposta.stop_reason != "tool_use":
    #        -> o agente terminou. Imprima o texto final e dê 'break'.
    #
    #   3. SENÃO (o modelo quer usar ferramenta(s)):
    #        a. Anexe a fala do modelo ao histórico:
    #             mensagens.append({"role": "assistant", "content": resposta.content})
    #        b. Para CADA bloco com .type == "tool_use" na resposta.content:
    #             - leia bloco.name e bloco.input
    #             - execute a função via FUNCOES[bloco.name](**bloco.input)
    #             - monte um dict tool_result com "tool_use_id" = bloco.id
    #               e "content" = resultado
    #        c. Anexe TODOS os tool_results numa única mensagem "user":
    #             mensagens.append({"role": "user", "content": [<lista de tool_results>]})
    #
    #   4. O loop repete: o modelo agora vê o resultado e decide o próximo passo.
    #
    # DICA: um turno pode pedir MAIS DE UMA ferramenta. Itere todos os blocos
    #       tool_use antes de voltar ao topo do loop.
    # DICA: use um contador de segurança (ex: máx. 10 voltas) para evitar
    #       loops infinitos enquanto você depura.
    # =========================================================================
    pass  # <-- apague e escreva seu loop aqui


if __name__ == "__main__":
    main()
