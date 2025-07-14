import os
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# .envファイルからAPIキーを取得
openai_api_key = os.getenv("OPENAI_API_KEY")

# APIキーが存在するか確認
if not openai_api_key:
    print("エラー: OPENAI_API_KEYが.envファイルに設定されていません。")
    print("ファイルが存在し、正しい変数名でキーが記述されているか確認してください。")
else:
    try:
        # OpenAIクライアントを初期化
        client = OpenAI(api_key=openai_api_key)

        # 試しに簡単なチャット完了リクエストを送信
        # 使用するモデルは、あなたの環境で利用可能なものを指定してください
        # 例: "gpt-3.5-turbo", "gpt-4", "gpt-4o"
        print(f"モデル '{'gpt-4'}' でAPIキーを検証中...")
        response = client.chat.completions.create(
            model="gpt-4", # もしこれがエラーになるなら "gpt-4o" など他のモデルを試す
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, world!"}
            ],
            max_tokens=10 # 短い応答を期待
        )

        # 応答が成功した場合
        print("\n--- APIキーは有効です ---")
        print("APIからの応答例:")
        print(response.choices[0].message.content)

    except Exception as e:
        # エラーが発生した場合
        print("\n--- APIキーが無効であるか、またはAPIアクセスに問題があります ---")
        print(f"エラー詳細: {e}")

        # 特に'AuthenticationError'はキーの問題を示唆
        if "AuthenticationError" in str(e):
            print("考えられる原因: APIキーが間違っている、または無効です。")
            print("OpenAI PlatformでAPIキーを再生成し、.envファイルを更新してください。")
        elif "insufficient_quota" in str(e) or "rate limit" in str(e):
            print("考えられる原因: 無料枠を使い切ったか、短期間のレート制限に引っかかっています。")
            print("OpenAI PlatformのUsageページを確認するか、しばらく待ってから再試行してください。")
        elif "The model `xxx` does not exist" in str(e):
            print("考えられる原因: 指定したモデル名が間違っているか、利用できません。")
            print("OpenAI PlatformのModelsページで利用可能なモデルを確認してください。")