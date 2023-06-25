# -*- coding: utf-8 -*-
"""
cron: 0 0 0 * * *
new Env('HiFiNi');
"""

import json
from sendNotify import send
import requests
import re
import os
import sys
requests.packages.urllib3.disable_warnings()


def start(cookie):
    try:
        sign_in_url = "https://www.hifini.com/sg_sign.htm"
        headers = {
            'Cookie': cookie,
            'authority': 'www.hifini.com',
            'accept': 'text/plain, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'https://www.hifini.com',
            'referer': 'https://www.hifini.com/',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        rsp = requests.post(url=sign_in_url, headers=headers,
                            timeout=15, verify=False)
        rsp_text = rsp.text.strip()
        print(rsp_text)
        if "今天已经签过啦！" in rsp_text:
            msg = '已经签到过了，不再重复签到!'
        elif "成功" in rsp_text:
            msg = "签到成功!"
        elif "503 Service Temporarily" in rsp_text:
            msg = "服务器异常！"
        elif "请登录后再签到!" in rsp_text:
            msg = "Cookie没有正确设置！"
        else:
            msg = "未知异常!"

        # rsp_json = json.loads(rsp_text)
        # print(rsp_json['code'])
        # print(rsp_json['message'])
        print("签到结果: ",msg)
        send("hifini 签到结果", msg)
    except Exception as e:
        print("签到失败，失败原因:"+str(e))
        send("hifini 签到结果", str(e))


if __name__ == "__main__":
    cookie = os.getenv("HIFINI_COOKIE")
    start(cookie)
