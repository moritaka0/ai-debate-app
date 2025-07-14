import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# .envファイルを読み込む
load_dotenv()

app = Flask(__name__)
CORS(app) # CORSを有効にする

# 環境変数からAPIキーを取得
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") # .envではGEMINI_API_KEYとしていました
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Gemini APIの設定
genai.configure(api_key=GOOGLE_API_KEY)
# Geminiモデルを 'models/gemini-1.5-flash' に変更
gemini_model_name = 'models/gemini-1.5-flash'


# OpenAI APIの設定
openai_client = OpenAI(api_key=OPENAI_API_KEY)
# GPTモデルを 'gpt-4' に変更
gpt_model_name = "gpt-4" # または 'gpt-4o'、'gpt-4-turbo' など、利用可能なバージョンに合わせる


@app.route('/api/start-debate', methods=['POST'])
def start_debate():
    data = request.json
    topic = data.get('topic')

    if not topic:
        return jsonify({"error": "議論のテーマが指定されていません"}), 400

    try:
        # Geminiで最初の発言を生成 (議論の導入)
        model = genai.GenerativeModel(gemini_model_name) # ここで新しいGeminiモデル名を使用
        convo_gemini = model.start_chat(history=[])
        initial_prompt = f"以下のテーマについて議論を開始します。あなたの最初の意見を述べてください。テーマ: {topic}"
        response_gemini = convo_gemini.send_message(initial_prompt)
        initial_gemini_text = response_gemini.text

        # 最初の発言のみを返す
        return jsonify({
            "initialMessage": {
                "speaker": "Gemini",
                "text": initial_gemini_text
            }
        })

    except Exception as e:
        print(f"議論開始エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-next-turn', methods=['POST'])
def generate_next_turn():
    data = request.json
    topic = data.get('topic')
    debate_history = data.get('debateHistory', []) # 現在の議論履歴を受け取る

    if not topic:
        return jsonify({"error": "議論のテーマが指定されていません"}), 400

    if not debate_history:
        return jsonify({"error": "議論履歴が空です。初期化されていません。"}), 400

    try:
        # --- GPTの発言を生成 ---
        gpt_messages = [
            {"role": "system", "content": f"あなたは'{topic}'についての議論に参加するAIです。簡潔かつ論理的に反論してください。"}
        ]
        # 過去の議論履歴をGPTのメッセージ形式に変換して追加
        for msg in debate_history:
            role = "user" if msg['speaker'] == "Gemini" else "assistant"
            gpt_messages.append({"role": role, "content": msg['text']})

        # GPTの最新の発言を生成
        completion = openai_client.chat.completions.create(
            model=gpt_model_name, # ここで新しいGPTモデル名を使用
            messages=gpt_messages,
            max_tokens=150, # ここで文字数を制限
        )
        gpt_text = completion.choices[0].message.content

        # --- Geminiの発言を生成 ---
        # Geminiのチャット履歴を構築
        gemini_history_for_turn = []
        for msg in debate_history:
            # Gemini APIは 'user' と 'model' ロールを使用
            # userがAIからの応答、modelがAI自身の応答
            gemini_history_for_turn.append({"role": "user" if msg['speaker'] != "Gemini" else "model", "parts": [{"text": msg['text']}]})
            
        # GPTの最新の発言をGeminiの履歴に追加 (GeminiはGPTの発言に対して応答する)
        # 重要なのは、Geminiのモデルへの指示が適切に渡されるようにすること
        # initial_prompt_gemini の内容をここでも踏襲
        # 最新のGPTの応答がユーザーからのメッセージとして渡される
        
        # モデルを再初期化（履歴を正しく引き継ぐため）
        model = genai.GenerativeModel(gemini_model_name) # ここで新しいGeminiモデル名を使用

        # チャットセッションを履歴付きで開始し、最新のGPT発言に返信する
        convo_gemini = model.start_chat(history=gemini_history_for_turn)
        response_gemini = convo_gemini.send_message(gpt_text)
        gemini_text = response_gemini.text


        # 生成されたGPTとGeminiの発言を返す
        return jsonify({
            "newMessages": [
                {"speaker": "GPT", "text": gpt_text},
                {"speaker": "Gemini", "text": gemini_text}
            ]
        })

    except Exception as e:
        print(f"次のターン生成エラー: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)