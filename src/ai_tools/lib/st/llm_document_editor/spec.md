# LLM Document Editor

streamlit用。
ドキュメントの部分修正をLLMを使用しながら行うエディタ。

- 引数
  - document:str
    - 対象のドキュメント。
  - extra_context:str
    - LLMに送る追加コンテキスト。
  - on_change:Callable
    - 編集が実行されたあと呼び出される。修正されたdocumentが送られる。
- 左カラム
  - ビューワー。markdown_viewerを使用してデータを見る。
  - 直接編集できるようにedit機能を有効にする。
- 右カラム
  - 対象入力欄（テキストエリア）
    - 編集対象のテキストをビューワーからコピペする。
  - プロンプト欄（テキストエリア）
    - どう編集すべきか入力する
  - 実行ボタン
    - 編集を実行する
- 編集プロセス
  - structured_askで問い合わせてEditResponseとして結果を受け取る
  - LLMTextEditorで編集を実行する。
