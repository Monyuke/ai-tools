# editツール

## EditData

Pydantic BaseModel で定義。

- file: ファイルの絶対パス
- search: 置換対象の文字列（完全一致が必要）。新規作成や削除の場合は空。
- replace: 置換後の文字列。削除では空。
- type: Create, Edit, Delete

structured outputで出力させる。

## build_edit_data_list() -> List[EditData]

- ユーザープロンプトを受け取る。
- src/ai_tools/lib/llm/__init__.py structured_askを使用してEditDataを生成させる。

## edit()

- EditDataを受け取る。
- 指定されたファイルで編集を行う。
- ファイルが存在する場合は置換を行う。
- ファイルが存在しない場合は新規作成し書き込む。

## edit_all()

- EditDataのリストを受け取り全てedit()する。
