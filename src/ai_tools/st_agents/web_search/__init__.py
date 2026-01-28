import streamlit as st
from ai_tools.lib.llm import simple_ask, structured_ask, tool_call
from ai_tools.tools.web_search import web_tools
from textwrap import dedent
from time import sleep
from pydantic import BaseModel, Field
from typing import Optional, List

"""
Web検索エージェント。
"""

model = "gpt-oss:20b"


class Information(BaseModel):
    url: str = Field(default="no url", description="URL")
    title: str = Field(default="no title", description="Title")
    body: str = Field(default="no body", description="Body")


class SearchResults(BaseModel):
    results: List[Information] = Field(default=[], description="検索結果")

class Document(BaseModel):
    title: str = Field(default="no title", description="Title")
    body: str = Field(default="no body", description="Body")

def st_agent_websearch(user_message: str) -> Document:
    result = ""
    with st.status("検索中...", expanded=False) as status:
        st.write("開始")

        st.write("情報の収集")
        search_result = tool_call(
            model=model,
            reasoning="low",
            tools=web_tools,
            message=dedent(
                f"""\
                ユーザー要求を直接的に満たすためにWeb検索を行い情報を収集せよ。
                
                ユーザー要求：
                {user_message}
                """
            ),
        )

        st.write("ドキュメント化")
        response = structured_ask(
            model,
            dedent(
                f"""\
                    集められた情報から、ユーザーの要求を満たすドキュメントを作成しろ。
                    なお、ユーザーが要求しているのは特別な指示がない限り、詳細なコードではなく定義と概略である。実装手順はお前には聞いてない。
                    お前の考えた手順は低品質かつ無意味だから出すな。一般的に行われている内容を探せ。
                    検索結果に含まれない情報は一切出力してはならない。

                    見やすい形で整形し出力せよ。
                    表は見づらいので単純なデータの列挙でのみ許可。
                    基本的には見出しと文章で説明せよ。

                    最後には必ず出典一覧をつけること。タイトル：URL形式。

                    ユーザー要求：
                    {user_message}

                    情報：
                    {search_result}
                    """
            ),
            schema=Document
        )
        st.write(response)
        sleep(1)

        status.update(label="完了", state="complete", expanded=False)
        result = response
    return result
