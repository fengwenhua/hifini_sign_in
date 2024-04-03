# -*- coding: utf-8 -*-
"""
cron: 1 0 0 * * *
new Env('HiFiNi');
"""

import json
# from sendNotify import send  # 本地调试用
from notify import send  # 导入青龙后自动有这个文件
from bs4 import BeautifulSoup
import requests
import re
import os
import sys
import time
requests.packages.urllib3.disable_warnings()


def start(cookie):
    max_retries = 5
    retries = 0
    msg = ""
    while retries < max_retries:
        try:
            msg += "第{}次执行签到\n".format(str(retries+1))
            sign_in_url = "https://www.hifini.com/sg_sign.htm"
            headers = {
                'Cookie': cookie,
                'authority': 'www.hifini.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9,und;q=0.8',
                'referer': 'https://www.hifini.com/',
                'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'sec-gpc': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            }
            
            rsp = requests.get(url=sign_in_url, headers=headers, timeout=15, verify=False)
            rsp_text = rsp.text
            success = False

            # 判断签到结果
            if "请登录后查看" in rsp_text:
                msg += "Cookie没有正确设置！\n"
                success = True
            elif "今日排名" in rsp_text:
                # 匹配签到结果
                soup = BeautifulSoup(rsp_text, 'html.parser')
                table = soup.find('table')  # 找到第一个表格
                rows = table.find_all('tr')  # 获取所有行
                last_row = rows[-1]  # 获取最后一行

                # 提取最后一行的所有单元格内容
                cells = last_row.find_all('td')
                last_row_content = [cell.text for cell in cells]

                msg += "账户 {} hifini签到成功！\n今日签到排名{}名，本次签到获得{}，现有{}，已连续签到{}。".format(
                    last_row_content[1], last_row_content[0], last_row_content[3],
                    last_row_content[2], last_row_content[-1]
                )
                success = True
            elif "503 Service Temporarily" in rsp_text or "502 Bad Gateway" in rsp_text:
                msg += "服务器异常！\n"
            else:
                msg += "未知异常!\n"
                msg += rsp_text + '\n'

            # 发送消息
            if success:
                print("签到结果: ",msg)
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
    start(cookie)
