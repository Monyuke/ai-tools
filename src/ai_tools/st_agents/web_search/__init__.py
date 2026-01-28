import streamlit as st
from ai_tools.lib.llm import simple_ask
from ai_tools.tools.web_search import web_tools
from textwrap import dedent
from time import sleep

"""
Web検索エージェント。

以下の手順で進める。

- ユーザーの要求を具体化
  - 欠落している情報はなにか
- ユーザーの要求を検索するための前提条件を収集
- 前提条件を元に要求の解決方法を収集
- 収集結果を要求にあわせてまとめる
- チェック
  - まとめた内容が収集内容と矛盾していないか
  - ユーザの要求を満たしているか
- 満たしていたら結果を返す
- 駄目なら再度実行

"""

model = "gpt-oss:20b"


def st_agent_websearch(user_message: str) -> str:
    result = ""
    with st.status("検索中...", expanded=False) as status:
        st.write("開始")


        st.write("情報の収集")
        response = simple_ask(
            model,
            dedent(
                f"""\
                    ユーザー要求を直接的に満たすために情報を収集せよ。内部知識は極力つかわず、Web検索を行い情報を収集せよ。
                    なお、ユーザーが要求しているのは特別な指示がない限り、詳細なコードではなく定義と概略である。実装手順はお前には聞いてない。
                    お前の考えた手順は低品質かつ無意味だから出すな。一般的に行われている内容を探せ。

                    見やすい形で整形し出力せよ。
                    表は見づらいので単純なデータの列挙でのみ許可。
                    基本的には見出しと文章で説明せよ。

                    ユーザー要求：
                    {user_message}
                    """
            ),
            tools=web_tools
        )
        st.write(response)
        sleep(1)

        # st.write("情報の成形")
        # response = simple_ask(
        #     model,
        #     dedent(
        #         f"""\
        #             与えられた情報を、ユーザー要求を直接的に満たし、かつ見やすい形で整形し出力せよ。
        #             表は見づらいので単純なデータの列挙でのみ許可。
        #             基本的には見出しと文章で説明せよ。

        #             ユーザー要求：
        #             {user_message}

        #             情報：
        #             {response}
        #             """
        #     ),
        # )
        # st.write(response)
        # sleep(1)


        status.update(label="完了", state="complete", expanded=False)
        result = response
    return result
