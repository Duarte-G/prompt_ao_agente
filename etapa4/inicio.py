"""
ETAPA 4 — Mão livre: estenda o agente!
======================================

Este arquivo é uma CÓPIA do agente 100% funcional da Etapa 3. Todos partem de
um motor ReAct que já funciona. Sua missão é adicionar NOVAS ferramentas.

Para cada ferramenta nova, lembre-se de fazer as 3 coisas:
    1. Escrever a função Python.
    2. Registrá-la no dicionário FUNCOES.
    3. Descrever o schema dela na lista TOOLS.
(O loop do agente NÃO precisa mudar — é genérico de propósito!)

------------------------------------------------------------------------------
DESAFIOS (escolha conforme seu ritmo):

  [INICIANTE]   gerar_saudacao_personalizada(nome)
                Recebe um nome e devolve uma saudação simpática.
                Teste com um PEDIDO tipo: "Crie uma saudação para a Ana".

  [INTERMEDIÁRIO]  agendar_evento(titulo, data)
                Salva o evento numa nova linha de 'agenda.csv'
                (crie o cabeçalho se o arquivo não existir).
                Teste: "Agende a reunião de equipe para 2025-07-01".

  [AVANÇADO]    Memória local com 'memoria.json'
                Crie ferramentas para LER e ESCREVER fatos num memoria.json,
                para o agente lembrar de coisas entre execuções.
                Teste: "Lembre que meu aniversário é em março" e, depois,
                       "Qual o mês do meu aniversário?".
------------------------------------------------------------------------------

Uso:
    python inicio.py
"""

import os

import requests
from dotenv import load_dotenv
import anthropic

MODELO = "claude-haiku-4-5"

PEDIDO = "Qual o clima no CEP 01310-100? Salve em previsao.txt"

# Trava de segurança: impede loop infinito caso algo dê errado.
MAX_ITERACOES = 10


# =============================================================================
# As ferramentas do agente. Adicione as suas aqui!
# =============================================================================
def buscar_cep(cep: str) -> str:
    """Descobre a cidade a partir do CEP — versão MOCK (offline) para o workshop.

    Em redes corporativas o HTTPS costuma ser interceptado (proxy com
    certificado próprio), o que quebra a chamada real ao ViaCEP. Para a demo
    funcionar em qualquer rede, usamos um mapa fixo. A versão com a API real
    está logo abaixo, comentada — descomente fora de redes com proxy de SSL.
    """
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    cidades = {
        "01310100": "São Paulo",
        "80010000": "Curitiba",
        "87010000": "Maringá",
    }
    return cidades.get(cep_limpo, f"CEP {cep} não encontrado.")

    # --- Versão real do ViaCEP (requer internet sem interceptação de SSL) ----
    # try:
    #     resp = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=10)
    #     dados = resp.json()
    #     if dados.get("erro"):
    #         return f"CEP {cep} não encontrado."
    #     return dados.get("localidade", "cidade desconhecida")
    # except requests.RequestException as e:
    #     return f"Erro ao consultar o CEP: {e}"


def get_clima(cidade: str) -> str:
    """Simula a consulta a uma API de clima."""
    return "25 graus e ensolarado"


def salvar_arquivo(nome_arquivo: str, conteudo: str) -> str:
    """Salva o conteúdo em um arquivo de texto."""
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Arquivo '{nome_arquivo}' salvo com sucesso."


FUNCOES = {
    "buscar_cep": buscar_cep,
    "get_clima": get_clima,
    "salvar_arquivo": salvar_arquivo,
    # <-- registre suas novas ferramentas aqui
}


# =============================================================================
# Os schemas que o modelo enxerga. Adicione o schema das suas ferramentas!
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
    # <-- descreva suas novas ferramentas aqui
]


def main() -> None:
    load_dotenv()
    client = anthropic.Anthropic()

    mensagens = [{"role": "user", "content": PEDIDO}]

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


if __name__ == "__main__":
    main()
