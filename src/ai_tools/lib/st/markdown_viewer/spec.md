# Markdown Viewer

- streamlit用の簡易カスタムMarkdown Viewer
- 関数として作る
- コンポーネントとしてコンテナとしてまとめる。
- ボタンでタブを作る。
  - Preview
    - st.markdownで表示する
  - Code
    - st.codeで表示する。
  - Edit
    - st.text_areaで表示する。
    - 引数on_changeがNoneなら表示しない。
- 引数
  - body:str
  - on_change:Optional[Callable]
