import streamlit as st
import openai
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import re

# -------------------- UI --------------------
st.set_page_config(page_title="面接評価AIアプリ", layout="centered")
st.title("🎯 採用AI評価アプリ")
st.markdown("---")

# APIキー入力
api_key = st.text_input("🔑 OpenAI APIキーを入力してください", type="password")

# ファイルアップロード
txt_file = st.file_uploader("📝 面接文字起こし（.txt）ファイルをアップロードしてください", type=["txt"])

# 評価ボタン
if st.button("▶️ 評価する") and api_key and txt_file:
    # OpenAIクライアント初期化
    client = openai.OpenAI(api_key=api_key)

    # アップロードされたテキストを読み込む
    content = txt_file.read().decode("utf-8")

    # カスタム評価指標に基づくプロンプト
    prompt = f"""
以下の面接内容を、以下の4つの観点でそれぞれ10点満点で評価し、点数とその理由をコメントしてください：

1. 胆力：粘着力、修羅場処理、長期戦が得意、決断して耐久して突破する力
2. 好奇心：新市場をかぎつける力、学習サイクルが高速、短期戦が得意、発見して学習して拡張する
3. 論理性：話の構成、理由や根拠の明示、具体例が含まれているか
4. 協調性：他者との信頼関係、チーム行動、対話への柔軟性があるか

回答は以下の形式で出力してください：
```
胆力：7点（理由）
好奇心：8点（理由）
論理性：6点（理由）
協調性：7点（理由）
```

【面接内容】
{content}
"""

    # ChatGPT API呼び出し（v1対応）
    with st.spinner("ChatGPTが評価中です..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

    result_text = response.choices[0].message.content
    st.success("✅ 評価が完了しました！")

    # 結果の表示
    st.markdown("### 📋 評価結果")
    st.text(result_text)

    # スコア抽出とレーダーチャート描画
    try:
        scores = {}
        for line in result_text.splitlines():
            match = re.match(r"(.*)：(\d+)点", line)
            if match:
                category = match.group(1).strip()
                score = int(match.group(2))
                scores[category] = score

        if scores:
            st.markdown("### 📈 レーダーチャート")
            labels = list(scores.keys())
            values = list(scores.values())
            values += values[:1]
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            ax.plot(angles, values, 'o-', linewidth=2, color='orange')
            ax.fill(angles, values, alpha=0.25, color='orange')
            ax.set_thetagrids(np.degrees(angles[:-1]), labels)
            ax.set_ylim(0, 10)
            ax.set_title("面接評価レーダーチャート", size=16)
            st.pyplot(fig)
    except Exception as e:
        st.error("⚠️ グラフの生成に失敗しました。出力形式をご確認ください。")
