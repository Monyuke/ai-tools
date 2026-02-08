from typing import List, Any, Optional, Dict
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from pprint import pprint
import json
from textwrap import dedent
from langchain_core.messages import messages_to_dict


def simple_ask(model: str, message: str, reasoning="low", tools: List[Any] = []) -> str:
    if "gpt-oss" not in model:
        reasoning = None
    llm = ChatOllama(
        model=model,
        reasoning=reasoning,
        # 返答の固定度があがる。
        temperature=0,
        top_p=1.0,
        top_k=0,
    )
    agent = create_agent(model=llm, tools=tools)
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    _message = result["messages"][-1]
    return _message.content


def structured_ask(model: str, message: str, schema: Any, reasoning="low") -> Any:
    if "gpt-oss" not in model:
        reasoning = None
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
    if "gpt-oss" not in model:
        reasoning = None
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


def chat(
    model: str,
    messages: List[Dict[str, str]],
    reasoning: Optional[str] = "low",
    tools: List[Any] = [],
) -> List[Dict[str, str]]:
    """
    複数メッセージを受け取り、LLM で応答を生成する関数。

    Parameters
    ----------
    model : str
        使用する LLM モデル名。例: "gpt-oss"、"llama3.1" など。
    messages : List[Dict[str, str]]
        送信するメッセージのリスト。各メッセージは
        {"role": "user" | "assistant" | "system", "content": str} で表現。
    reasoning : str, optional
        推論レベル。デフォルトは "low"。`model` が "gpt-oss" でない場合は
        None に設定され、推論は無効化される。
    tools : List[Any], optional
        エージェントに渡すツール。デフォルトは空リスト。

    Returns
    -------
    List[Dict[str, str]]
        LLM が返したメッセージのリスト。各メッセージは
        {"role": "assistant" | "user" | "system", "content": str} で表現。
    """
    # 推論設定は gpt-oss のみ有効
    if "gpt-oss" not in model:
        reasoning = None

    llm = ChatOllama(
        model=model,
        reasoning=reasoning,
        temperature=0,
        top_p=1.0,
        top_k=0,
    )

    # エージェントを作成
    agent = create_agent(model=llm, tools=tools)

    # 受け取ったメッセージをそのまま渡す
    result = agent.invoke({"messages": messages})

    # messages_to_dictの結果を {"role": ..., "content": ...} 形式に変換
    converted_messages = []
    for msg_dict in messages_to_dict(result["messages"]):
        msg_type = msg_dict["type"]

        # typeをroleに変換
        if msg_type == "human":
            role = "user"
        elif msg_type == "ai":
            role = "assistant"
        elif msg_type == "system":
            role = "system"
        elif msg_type == "tool":
            role = "tool"
        else:
            role = msg_type

        converted_messages.append(
            {"role": role, "content": msg_dict["data"]["content"]}
        )

    return converted_messages
