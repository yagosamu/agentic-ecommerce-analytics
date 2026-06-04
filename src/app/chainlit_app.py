import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import chainlit as cl
from agent.shopagent import create_shopagent

WELCOME = """\
Ola! Sou o **ShopAgent**.

Tenho acesso a duas fontes de dados:
- **The Ledger** *(Postgres)*: faturamento, pedidos, produtos, ticket medio
- **The Memory** *(Qdrant)*: reclamacoes, sentimentos, temas de reviews

Decido sozinho qual fonte consultar. Basta fazer sua pergunta em portugues.

**Exemplos:**
- *"Qual o faturamento por estado?"*
- *"O que os clientes reclamam sobre entrega?"*
- *"Top 3 estados com mais reclamacoes e seu faturamento"*
"""


@cl.on_chat_start
async def on_start():
    agent = create_shopagent()
    thread_id = str(uuid4())
    cl.user_session.set("agent", agent)
    cl.user_session.set("thread_id", thread_id)
    await cl.Message(content=WELCOME).send()


@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")
    config = {"configurable": {"thread_id": cl.user_session.get("thread_id")}}

    final_msg = cl.Message(content="")
    step_map: dict[str, cl.Step] = {}

    try:
        async for chunk in agent.astream(
            {"messages": [{"role": "user", "content": message.content}]},
            config=config,
            stream_mode="updates",
        ):
            for node, data in chunk.items():
                for msg in data.get("messages", []):

                    # Tool calls (from model node) — open a step for each
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            step = cl.Step(name=tc["name"], type="tool")
                            step.input = str(tc["args"])[:600]
                            await step.send()
                            step_map[tc["id"]] = step

                    # Tool results — close the corresponding step
                    elif hasattr(msg, "type") and msg.type == "tool" and msg.content:
                        step = step_map.get(getattr(msg, "tool_call_id", ""))
                        if step:
                            step.output = str(msg.content)[:800]
                            await step.update()

                    # Final AI response (no tool_calls, from model node)
                    elif (
                        node == "model"
                        and hasattr(msg, "content")
                        and not getattr(msg, "tool_calls", None)
                    ):
                        content = msg.content
                        if isinstance(content, list):
                            content = "".join(
                                b.get("text", "") for b in content if isinstance(b, dict)
                            )
                        if content:
                            final_msg.content = content

    except Exception as e:
        final_msg.content = f"Erro ao processar sua pergunta: {type(e).__name__}: {e}"

    await final_msg.send()
