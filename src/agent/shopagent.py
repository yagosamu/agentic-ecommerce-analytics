import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

import os

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver

from agent.tools import TOOLS

DEFAULT_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Voce e o ShopAgent, um assistente analitico especializado neste e-commerce brasileiro.

Voce tem acesso a duas fontes de dados:
- supabase_execute_sql: dados exatos, como faturamento, pedidos, produtos e clientes (SQL)
- qdrant_semantic_search: experiencia do cliente, como reviews, reclamacoes e sentimentos (busca semantica)

Regras:
- Para numeros, contagens ou rankings: use supabase_execute_sql com SQL preciso
- Para reclamacoes, sentimento ou temas: use qdrant_semantic_search com descricao natural
- Para perguntas hibridas: use ambas as ferramentas em sequencia
- Se nao tiver dados suficientes, diga claramente

Responda sempre em portugues, de forma clara e objetiva.
Formate tabelas em markdown quando apresentar multiplas linhas de dados."""


def create_shopagent():
    model = os.getenv("SHOPAGENT_MODEL", DEFAULT_MODEL)
    llm = ChatAnthropic(model=model, temperature=0)
    memory = MemorySaver()
    return create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )


def run_with_trace(agent, question: str, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    print(f"\n{'='*60}")
    print(f"Pergunta: {question}")
    print('='*60)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
    )

    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"\n  [Action] {tc['name']}")
                print(f"  [Input]  {str(tc['args'])[:300]}")
        elif hasattr(msg, "type") and msg.type == "tool" and msg.content:
            print(f"  [Observation] {str(msg.content)[:300]}")

    output = result["messages"][-1].content
    print(f"\n  [Final Answer]\n{output}")
    return output


if __name__ == "__main__":
    import time
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    agent = create_shopagent()

    questions = [
        "Qual o faturamento total por estado?",
        "Quais clientes reclamam de entrega atrasada?",
        "Top 3 estados com mais reclamacoes e seu faturamento",
    ]

    for i, q in enumerate(questions):
        if i > 0:
            print("\n[aguardando 30s para evitar rate limit...]\n")
            time.sleep(30)
        run_with_trace(agent, q, thread_id=str(uuid4()))
