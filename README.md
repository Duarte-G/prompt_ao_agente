# 🤖 Do Prompt ao Agente

Um material didático prático para sair de um **prompt simples** até um **agente autônomo** (padrão ReAct) usando Python e a API da Anthropic.

A trilha é dividida em 4 etapas. Cada uma introduz **um** conceito novo, sempre com dois arquivos:

- **`inicio.py`** → o esqueleto, com blocos `TODO` para você completar.
- **`solucao.py`** → a versão completa e funcional (o gabarito).

---

## 🚀 Setup (faça uma vez)

> Requisitos: Python 3.10+ e uma chave da API da Anthropic ([gere aqui](https://console.anthropic.com/settings/keys)).

```powershell
# 1. Crie e ative um ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows (PowerShell)
# source .venv/bin/activate         # Linux / macOS

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure sua chave
Copy-Item .env.example .env         # depois edite .env e cole sua chave real

# 4. Valide o ambiente
python check_setup.py               # deve imprimir: OK!
```

Se aparecer **`OK!`**, está tudo certo para começar. 🎉

---

Aqui: sk-an t-api03 -8pjFZQvP72t2tURN9MU  wesaoHMznhYpGSFewEvZ4o4OcKiYX1ES9AMhXm0X97e8JH2dAGhQ GPIrRIZLuOEjq9A-AGt00wAA

## 🗺️ A Trilha

| Etapa | Conceito | O que você aprende |
|-------|----------|--------------------|
| **1** | System Prompt | Forçar o modelo a extrair dados e devolver **JSON puro** |
| **2** | Tool Calling | Conectar o modelo a uma **função Python real** |
| **3** | Loop ReAct | O **agente autônomo** que encadeia várias ferramentas |
| **4** | Mão livre | **Estender** o agente com suas próprias ferramentas |

### Etapa 1 — O poder do System Prompt
O modelo lê um texto desestruturado (*"vai chover em Maringá amanhã?"*) e devolve **estritamente** um JSON com `cidade`, `data_relativa` e `intencao`. Sem ferramentas — só o contrato do system prompt e `temperature=0`.

📁 [`etapa1/`](etapa1/)

### Etapa 2 — Tool Calling
A intenção extraída vira **ação**: o modelo decide chamar a função `get_clima()`. Você aprende o ciclo de 4 passos — o modelo pede a ferramenta → seu código executa → devolve o `tool_result` → o modelo formula a resposta final.

📁 [`etapa2/`](etapa2/)

### Etapa 3 — O Loop ReAct (o clímax)
Um pedido complexo: *"Qual o clima no CEP 01310-100? Salve em previsao.txt"*. O agente encadeia **3 ferramentas** sozinho (`buscar_cep` → `get_clima` → `salvar_arquivo`) dentro de um loop **Raciocínio → Ação → Observação**, até concluir.

📁 [`etapa3/`](etapa3/)

### Etapa 4 — Mão livre
Você parte de um agente **100% funcional** (cópia da solução da Etapa 3) e adiciona ferramentas novas. O motor do loop **não muda** — é genérico de propósito. Três níveis de desafio:

- 🟢 **Iniciante:** `gerar_saudacao_personalizada(nome)`
- 🟡 **Intermediário:** `agendar_evento(titulo, data)` → salva em `agenda.csv`
- 🔴 **Avançado:** memória local lendo/escrevendo em `memoria.json`

📁 [`etapa4/`](etapa4/)

---

## ▶️ Como rodar cada etapa

Tente primeiro o `inicio.py` (complete os `TODO`s). Se travar, compare com o `solucao.py`.

```powershell
python etapa1\inicio.py
python etapa1\solucao.py
```

---

## 📂 Estrutura do projeto

```
do-prompt-ao-agente/
├── requirements.txt
├── .env.example          # template da chave (copie para .env)
├── check_setup.py        # valida o ambiente
├── README.md
├── etapa1/               # System Prompt → JSON
│   ├── inicio.py
│   └── solucao.py
├── etapa2/               # Tool Calling
│   ├── inicio.py
│   └── solucao.py
├── etapa3/               # Loop ReAct
│   ├── inicio.py
│   └── solucao.py
└── etapa4/               # Estenda o agente
    ├── inicio.py
    └── solucao.py
```

---

## 🧠 O padrão ReAct, em uma frase

> O agente **Raciocina** sobre o próximo passo, **Age** chamando uma ferramenta, **Observa** o resultado — e repete o ciclo até resolver a tarefa.

Esse loop simples é o coração de praticamente todo agente de IA moderno. Ao final do workshop, você terá construído um do zero. 🚀

---

## ℹ️ Notas técnicas

- **Modelo usado:** `claude-haiku-4-5` — rápido, barato e confiável em loops com ferramentas.
- **A API é stateless:** todo o histórico (`mensagens`) é reenviado a cada chamada. É por isso que o loop sempre anexa as falas e os `tool_result` à lista.
- **Nunca versione o `.env`** — ele contém sua chave secreta.
