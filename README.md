# error_codes

エラーコードとその説明を JSON で出力します。

## 出力形式

```json
{
  "errors": [
    {
      "code": 0,
      "alias": "ERROR_SUCCESS",
      "description": "The operation completed successfully."
    },
    {
      "code": 1,
      "alias": "ERROR_INVALID_FUNCTION",
      "description": "Incorrect function."
    },
    ...
  ]
}
```

## 対応エラーコード

- Windows システムエラーコード
- errno

### Windows システムエラーコード

GetLastError の戻り値とその説明をまとめています。

### errno

Linux カーネルのエラーコードとその説明をまとめています。

## 開発

### 実行方法

[Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)をインストールし、以下の手順でビルドしてください。

1. VSCode で本プロジェクトを開き、[Dev Containers: Reopen in Container...]を実行してください。
1. `python app.py`を実行してください。
