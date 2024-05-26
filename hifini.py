# -*- coding: utf-8 -*-
"""
cron: 1 0 0 * * *
new Env('HiFiNi');
"""

import json
from sendNotify import send
import requests
import re
import os
import sys
import time
requests.packages.urllib3.disable_warnings()


def get_sign_value(cookies):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': cookies,
        'priority': 'u=0, i',
        'referer': 'https://www.hifini.com/sg_sign.htm',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    response = requests.get(
        'https://www.hifini.com/sg_sign.htm', headers=headers)
    # print(response.text)

    pattern = r'var sign = "([\da-f]+)"'
    matches = re.findall(pattern, response.text)

    if matches:
        sign_value = matches[0]
        print(sign_value)
        return sign_value
    else:
        if '登录后查看' in response.text:
            print("[-] Cookie失效")
            send("hifini 签到异常", "Cookie失效")
            return None
        print("No sign value found.")
        return None


def start(sign, cookie):
    max_retries = 20
    retries = 0
    msg = ""
    while retries < max_retries:
        try:
            msg += "第{}次执行签到\n".format(str(retries+1))
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

            data = {
                'sign': sign,
            }
            rsp = requests.post(url=sign_in_url, headers=headers, data=data,
                                timeout=15, verify=False)
            rsp_text = rsp.text.strip()
            print(rsp_text)
            success = False
            if "今天已经签过啦！" in rsp_text:
                msg += '已经签到过了，不再重复签到!\n'
                success = True
            elif "成功" in rsp_text:
                rsp_json = json.loads(rsp_text)
                msg += rsp_json['message']
                success = True
            elif "503 Service Temporarily" in rsp_text or "502 Bad Gateway" in rsp_text:
                msg += "服务器异常！\n"
            elif "请登录后再签到!" in rsp_text:
                msg += "Cookie没有正确设置！\n"
                success = True
            elif "操作存在风险，请稍后重试" in rsp_text:
                msg += "没有设置sign导致的!\n"
                success = False
                send("hifini 签到失败：", msg)
            else:
                msg += "未知异常!\n"
                msg += rsp_text + '\n'

            # rsp_json = json.loads(rsp_text)
            # print(rsp_json['code'])
            # print(rsp_json['message'])
            if success:
                print("签到结果: ", msg)
                send("hifini 签到结果", msg)
                break  # 成功执行签到，跳出循环
            elif retries >= max_retries:
                print("达到最大重试次数，签到失败。")
                send("hifini 签到结果", msg)
                break
            else:
                retries += 1
                print("等待20秒后进行重试...")
                time.sleep(20)
        except Exception as e:
            print("签到失败，失败原因:"+str(e))
            send("hifini 签到结果", str(e))
            retries += 1
            if retries >= max_retries:
                print("达到最大重试次数，签到失败。")
                break
            else:
                print("等待20秒后进行重试...")
                time.sleep(20)


if __name__ == "__main__":
    cookie = os.getenv("HIFINI_COOKIE")
    sign = get_sign_value(cookie)
    if sign:
        start(sign, cookie)
    else:
        send("hifini 签到异常", "hifini 签到失败：没有获取到签名，请联系开发人员")
