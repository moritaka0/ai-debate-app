import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv() # .envファイルを読み込む

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 利用可能なモデルを一覧表示する関数
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        # generateContent メソッドをサポートするモデルのみ表示
        print(f"Name: {m.name}, Display Name: {m.display_name}, Supported Methods: {m.supported_generation_methods}")