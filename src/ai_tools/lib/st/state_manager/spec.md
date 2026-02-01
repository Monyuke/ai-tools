# StateManager

- streamlit.session_state 内でデータ管理するクラス
- コンストラクタでkeyを受け取り、session_state[key] に情報を格納する。
- データの型はジェネリクスでdataclassを受け取る
- store, get, clear, serialize, deserializeメソッドを持つ
