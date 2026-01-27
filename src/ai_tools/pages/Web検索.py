import streamlit as st
from dataclasses import dataclass, field
from typing import List
from langchain_ollama import ChatOllama
from ai_tools.tools.web_search import web_search, find_in_page, fetch_webpage
from langchain.agents import create_agent


@dataclass
class AppState:
    # counter: int = 0
    # messages: List[str] = field(default_factory=list)
    ai_message: str = ""


if "state" not in st.session_state:
    st.session_state.state = AppState()

st.title("Web検索")
user_text = st.text_area("検索内容")

if st.button("検索"):
    # https://docs.langchain.com/oss/python/integrations/chat/ollama
    llm = ChatOllama(model="gpt-oss:20b", reasoning="low").bind_tools(
        [web_search, find_in_page, fetch_webpage]
    )
    agent = create_agent(
        model=llm, tools=[web_search, find_in_page, fetch_webpage]
    )
    print("user_text:" + str(user_text))
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"""全ての回答は必ず以下の形式で回答せよ。言語は日本語を使用すること。形式を満たさない回答は規律違反である。

形式：
# 調査結果
## 1.ユーザーの要求
＜ユーザーの要求を復唱＞
＜ユーザーの要求を直接的に満たす具体的な解釈＞

## 2.情報検索
### a.出典
＜ユーザー要求について検索。内部知識の利用不可＞

### b.要約
＜検索結果の要約＞

## 3.回答検証
＜要約がユーザーの要求を正しく満たしているか検証＞

形式を絶対に守ること。

質問：
{user_text}
""",
                }
            ]
        }
    )
    print('result:' + str(result))
    message = result["messages"][-1]
    print('message:' + str(message))
    print('message.content:' + str(message.content))
    st.session_state.state.ai_message = message.content


st.markdown(st.session_state.state.ai_message)
