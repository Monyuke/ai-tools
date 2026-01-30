from typing import List, Any
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from pprint import pprint
import json
from textwrap import dedent
from langchain_core.messages import messages_to_dict


def simple_ask(model: str, message: str, reasoning="low", tools: List[Any] = []) -> str:
    llm = ChatOllama(
        model=model, reasoning=reasoning, 
        # 返答の固定度があがる。
        temperature=0, top_p=1.0, top_k=0
    )
    agent = create_agent(model=llm, tools=tools)
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    _message = result["messages"][-1]
    return _message.content


def structured_ask(model: str, message: str, schema: Any, reasoning="low") -> Any:
    # agentだと構造化出力が使えない
    llm = ChatOllama(
        model=model, reasoning=reasoning, temperature=0, top_p=1.0, top_k=0
    )
    structured_llm = llm.with_structured_output(schema=schema)
    result = structured_llm.invoke(message)
    return result


def tool_call(
    model: str, message: str, reasoning="low", tools: List[Any] = []
) -> List[dict]:
    # agentだと構造化出力が使えないのでレスポンスから抽出する。
    llm = ChatOllama(
        model=model, reasoning=reasoning, temperature=0, top_p=1.0, top_k=0
    )
    agent = create_agent(
        model=llm,
        tools=tools,
    )
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": dedent(  # from textwrap import dedent
                        f"""\
                        {message}

                        出力は必ず
                        OK
                        のみにすること
                        """
                    ),
                }
            ]
        }
    )
    messages = messages_to_dict(result["messages"])
    print("messages:" + str(messages))

    tool_results = []
    for message in messages:
        if message["type"] != "tool":
            continue
        content = message["data"]["content"]  # こいつはstr！
        data = json.loads(content)
        tool_results.extend(data)

    return tool_results
