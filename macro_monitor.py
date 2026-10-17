import os
import requests
from icalendar import Calendar
from datetime import datetime, date

# ========== 配置区 ==========
# 替换webcal为https
ICLOUD_ICS_URL = "https://p223-caldav.icloud.com.cn/published/2/MTk4OTExMjI4MDE5ODkxMVecXgvgLp3mCu0m-AmkklVyzGnbk2R0xMHimM9yE5XiFatgsSwexKksc_n8SgjjQAe3kVtHUz3jva7B9cGLbdA"
SERVER_KEY = os.getenv("SERVER_SENDKEY")
REMIND_DAY = 3  # 提前3天提醒
# ============================

def fetch_ics_calendar(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    cal = Calendar.from_ical(resp.content)
    event_list = []
    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            event_start = component.get('dtstart').dt
            # 统一转date日期
            if isinstance(event_start, datetime):
                event_date = event_start.date()
            else:
                event_date = event_start
            event_list.append({
                "name": summary,
                "date": event_date
            })
    return event_list

def send_wx_msg(title, content):
    url = f"https://sctapi.ftqq.com/{SERVER_KEY}.send"
    data = {
        "title": title,
        "desp": content
    }
    requests.post(url, data=data)

if __name__ == "__main__":
    today = date.today()
    events = fetch_ics_calendar(ICLOUD_ICS_URL)
    for evt in events:
        delta = (evt["date"] - today).days
        if delta == REMIND_DAY:
            title = "【宏观监控告警】"
            msg = f"【事件预告】还有{REMIND_DAY}天：{evt['name']}，{evt['date']}"
            send_wx_msg(title, msg)
            print(f"触发推送: {msg}")