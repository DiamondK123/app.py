jieba.setLogLevel(20)  # 減少 log 噪音（可選）
jieba.initialize()

from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.graph_objs as go
import plotly.io as pio
import jieba
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    try:
        url = "https://www.ettoday.net/news/news-list.htm"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()  # 確保 HTTP 狀態為 200
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")

        titles = [t.text.strip() for t in soup.select(".part_list_2 h3 a") if t.text.strip()]
        if not titles:
            return "⚠️ 無法抓取 ETtoday 標題，網站可能結構已改變。"

        words = []
        for title in titles:
            segs = jieba.cut(title)
            words.extend([w for w in segs if len(w) > 1])

        counter = Counter(words)
        top_words = counter.most_common(10)

        df = pd.DataFrame(top_words, columns=["詞語", "次數"])
        fig = go.Figure([go.Bar(x=df["詞語"], y=df["次數"], marker_color='indigo')])
        fig.update_layout(title="ETtoday 熱門關鍵詞統計圖", xaxis_title="關鍵詞", yaxis_title="出現次數")
        plot_html = pio.to_html(fig, full_html=False)

        html_template = '''
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>ETtoday 關鍵詞統計</title></head>
        <body>
            <h2 style="text-align:center">🔥 ETtoday 熱門新聞即時爬蟲 + Plotly 圖表</h2>
            <div style="width:90%;margin:auto">{{ plot_div|safe }}</div>
        </body>
        </html>
        '''
        return render_template_string(html_template, plot_div=plot_html)

    except Exception as e:
        return f"<h3>❌ 程式錯誤：{str(e)}</h3>"

