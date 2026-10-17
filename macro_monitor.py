import yfinance as yf
import requests
import os

# 从GitHub的Secret读取密钥，不要写在这里！
SENDKEY = os.getenv("SERVER_SENDKEY")

# 风险阈值
VIX_THRESHOLD = 28
US10Y_THRESHOLD = 4.8
USDJPY_HIGH = 160
USDJPY_LOW = 152
WTI_OIL = 92

def send_wechat(msg):
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title":"宏观市场告警", "desp":msg}
    try:
        requests.post(url, data=data, timeout=15)
    except Exception as e:
        print("推送失败：", e)

def run_monitor():
    print("开始拉取宏观指标")
    alert_list = []
    try:
        # VIX恐慌指数
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="1d")
        vix_price = vix_data["Close"].iloc[-1]
        print(f"VIX={vix_price:.2f}")
        if vix_price >= VIX_THRESHOLD:
            alert_list.append(f"⚠️VIX恐慌指数触发 {vix_price:.2f}，超过阈值{VIX_THRESHOLD}")
    except Exception as e:
        print("VIX获取异常",e)

    try:
        # 美债10年期
        us10 = yf.Ticker("^TNX")
        us10_data = us10.history(period="1d")
        us10_price = us10_data["Close"].iloc[-1]
        print(f"10Y美债收益率={us10_price:.2f}")
        if us10_price >= US10Y_THRESHOLD:
            alert_list.append(f"⚠️10年期美债触发 {us10_price:.2f}，超过阈值{US10Y_THRESHOLD}")
    except Exception as e:
        print("美债获取异常",e)

    try:
        # USDJPY 美元兑日元
        usdjpy = yf.Ticker("USDJPY=X")
        usdjpy_data = usdjpy.history(period="1d")
        usdjpy_price = usdjpy_data["Close"].iloc[-1]
        print(f"USDJPY={usdjpy_price:.2f}")
        if usdjpy_price >= USDJPY_HIGH or usdjpy_price <= USDJPY_LOW:
            alert_list.append(f"⚠️USDJPY触发 {usdjpy_price:.2f}，区间突破")
    except Exception as e:
        print("USDJPY获取异常",e)

    try:
        # WTI原油
        wti = yf.Ticker("CL=F")
        wti_data = wti.history(period="1d")
        wti_price = wti_data["Close"].iloc[-1]
        print(f"WTI原油={wti_price:.2f}")
        if wti_price >= WTI_OIL:
            alert_list.append(f"⚠️WTI原油触发 {wti_price:.2f}，超过阈值{WTI_OIL}")
    except Exception as e:
        print("原油获取异常",e)

    if alert_list:
        content = "\n".join(alert_list)
        send_wechat(content)
        print("✅触发告警，微信推送已发送")
    else:
        print("✅ 当前所有指标正常，无警报")

if __name__ == "__main__":
    run_monitor()
