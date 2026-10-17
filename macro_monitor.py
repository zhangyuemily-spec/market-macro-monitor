import yfinance as yf
import requests
import ssl
import os
from datetime import datetime, date
from icalendar import Calendar

# 适配云端SSL
ssl._create_default_https_context = ssl._create_unverified_context

# ===================== 【配置区域】=====================
THRESHOLD = {
    "VIX": 28,          # VIX>28 触发警报
    "US10Y": 5.2,       # 10年期美债收益率>5.2才告警
    "USDJPY_UP": 160,   # USDJPY突破160，日元偏弱，留意干预预期
    "USDJPY_DROP": 152, # USDJPY跌到152以下 = 日元快速大涨，套息平仓红色警报
    "BRENT_OIL": 110    # 布伦特原油高于110
}
REMIND_DAY = 3
# iCloud ics链接（webcal改成https）
ICAL_URL = "https://p223-caldav.icloud.com.cn/published/2/MTk4OTExMjI4MDE5ODkxMVecXgvgLp3mCu0m-AmkklVyzGnbk2R0xMHimM9yE5XiFatgsSwexKksc_n8SgjjQAe3kVtHUz3jva7B9cGLbdA"
SENDKEY = os.getenv("SERVER_SENDKEY")
# ======================================================

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

        brent = yf.Ticker("BZ=F")
        data["brent"] = brent.info.get("regularMarketPrice")
    except Exception as e:
        print("拉取行情数据异常：", e)
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

def read_ical_events(url):
    """下载并解析iCloud日历，返回事件名称+日期"""
    events = []
    try:
        resp = requests.get(url, timeout=15)
        cal = Calendar.from_ical(resp.content)
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = component.get("summary")
                start_dt = component.get("dtstart").dt
                # 只保留date，忽略时分
                if isinstance(start_dt, datetime):
                    event_day = start_dt.date()
                else:
                    event_day = start_dt
                events.append({"name": str(summary), "date": event_day})
    except Exception as e:
        print("读取日历失败：", e)
    return events

def check_calendar_remind(events):
    remind_text = ""
    today = date.today()
    for evt in events:
        delta = (evt["date"] - today).days
        if delta == REMIND_DAY:
            remind_text += f"📅【事件预告】还有{REMIND_DAY}天：{evt['name']}，{evt['date']}\n"
    return remind_text

if __name__ == "__main__":
    print("开始拉取宏观指标...")
    raw_data = fetch_data()
    alert_msg = check_alert(raw_data)
    event_list = read_ical_events(ICAL_URL)
    calendar_msg = check_calendar_remind(event_list)

    final_msg = ""
    if alert_msg:
        final_msg += alert_msg
    if calendar_msg:
        final_msg += calendar_msg

    if final_msg:
        print("发现警报/事件提醒：\n", final_msg)
        send_wechat_alert(final_msg)
    else:
        print("✅ 当前所有指标正常，无警报，无临近宏观事件")