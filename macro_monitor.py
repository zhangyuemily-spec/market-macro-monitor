import yfinance as yf
import requests
import ssl
# 适配云端SSL
ssl._create_default_https_context = ssl._create_unverified_context

# ===================== 【这里修改你的阈值】=====================
THRESHOLD = {
    "VIX": 28,          # VIX>28 触发警报
    "US10Y": 4.8,       # 10年期美债收益率>4.8
    "USDJPY_UP": 160,   # USDJPY突破160，日元偏弱，留意干预预期
    "USDJPY_DROP": 152, # USDJPY跌到152以下 = 日元快速大涨，套息平仓红色警报
    "BRENT_OIL": 110    # 布伦特原油高于110
}
SENDKEY = "YOUR_SENDKEY"  # ← 替换这里！你的Server酱密钥
# ==============================================================

def send_wechat_alert(content):
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    params = {
        "title": "【宏观监控告警】",
        "desp": content
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        print("微信推送结果：", res.json())
    except Exception as e:
        print("推送失败", e)

def fetch_data():
    data = {}
    try:
        vix = yf.Ticker("^VIX")
        data["vix"] = vix.info.get("regularMarketPrice")

        us10 = yf.Ticker("^TNX")
        data["us10y"] = us10.info.get("regularMarketPrice")

        usdjpy = yf.Ticker("USDJPY=X")
        data["usdjpy"] = usdjpy.info.get("regularMarketPrice")

        # 布伦特原油 BZ=F
        brent = yf.Ticker("BZ=F")
        data["brent"] = brent.info.get("regularMarketPrice")
    except Exception as e:
        print("拉取数据异常：", e)
    return data

def check_alert(data):
    alert_text = ""
    v = data.get("vix")
    u10 = data.get("us10y")
    uj = data.get("usdjpy")
    oil = data.get("brent")

    if v and v > THRESHOLD["VIX"]:
        alert_text += f"🔴 VIX恐慌指数 {v:.2f}，突破{THRESHOLD['VIX']}\n"
    if u10 and u10 > THRESHOLD["US10Y"]:
        alert_text += f"🔴 10年期美债收益率 {u10:.2f}，突破{THRESHOLD['US10Y']}\n"
    if uj and uj > THRESHOLD["USDJPY_UP"]:
        alert_text += f"🟡 USDJPY {uj:.2f}，突破160，日元干预预期升温\n"
    if uj and uj < THRESHOLD["USDJPY_DROP"]:
        alert_text += f"🔴 USDJPY {uj:.2f}，快速下跌，日元暴涨！警惕套息平仓\n"
    if oil and oil > THRESHOLD["BRENT_OIL"]:
        alert_text += f"🟡 布伦特原油 {oil:.2f}，高于阈值{THRESHOLD['BRENT_OIL']}\n"

    return alert_text

if __name__ == "__main__":
    print("开始拉取宏观指标...")
    raw_data = fetch_data()
    alert_msg = check_alert(raw_data)
    if alert_msg:
        print("发现警报：\n", alert_msg)
        send_wechat_alert(alert_msg)
    else:
        print("✅ 当前所有指标正常，无警报")