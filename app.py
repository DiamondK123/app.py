import jieba
jieba.setLogLevel(20)
jieba.initialize()

from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    try:
        url = "https://tw.news.yahoo.com/"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")

        titles = [t.text.strip() for t in soup.select("h3") if t.text.strip()]
        if not titles:
            return "⚠️ 無法抓取 Yahoo奇摩新聞標題，網站可能結構已改變。"

        words = []
        for title in titles:
            segs = jieba.cut(title)
            words.extend([w for w in segs if len(w) > 1])

        counter = Counter(words)
        top_words = counter.most_common(10)

        df = pd.DataFrame(top_words, columns=["詞語", "次數"])

        bar_fig = go.Figure([go.Bar(x=df["詞語"], y=df["次數"], marker_color='indigo')])
        bar_fig.update_layout(title="Yahoo奇摩 熱門關鍵詞統計圖 (長條圖)", xaxis_title="關鍵詞", yaxis_title="出現次數")

        pie_fig = go.Figure([go.Pie(labels=df["詞語"], values=df["次數"], hole=0.3)])
        pie_fig.update_layout(title="Yahoo奇摩 熱門關鍵詞統計圖 (圓餅圖)")

        line_fig = go.Figure([go.Scatter(x=df["詞語"], y=df["次數"], mode='lines+markers')])
        line_fig.update_layout(title="Yahoo奇摩 熱門關鍵詞統計圖 (折線圖)", xaxis_title="關鍵詞", yaxis_title="出現次數")

        bar_html = pio.to_html(bar_fig, full_html=False)
        pie_html = pio.to_html(pie_fig, full_html=False)
        line_html = pio.to_html(line_fig, full_html=False)

        html_template = '''
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Yahoo奇摩 關鍵詞統計</title></head>
        <body>
            <h2 style="text-align:center">🔥 Yahoo奇摩新聞即時爬蟲 + Plotly 圖表</h2>
            <div style="width:90%;margin:auto">{{ bar_div|safe }}</div>
            <div style="width:90%;margin:auto;margin-top:50px">{{ pie_div|safe }}</div>
            <div style="width:90%;margin:auto;margin-top:50px">{{ line_div|safe }}</div>
        </body>
        </html>
        '''
        return render_template_string(html_template, bar_div=bar_html, pie_div=pie_html, line_div=line_html)

    except Exception as e:
        return f"<h3>❌ 程式錯誤：{str(e)}</h3>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
