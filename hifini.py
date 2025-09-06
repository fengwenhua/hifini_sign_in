# -*- coding: utf-8 -*-
"""
cron: 1 0 0 * * *
new Env('HiFiNi');
"""

import hashlib
import json
import os
import re
import time

import requests

from sendNotify import send

requests.packages.urllib3.disable_warnings()


def login(username, password):
    """
    登录HiFiNi网站
    :param username: 用户名
    :param password: 密码（明文，函数内部会进行MD5加密）
    :return: 登录成功返回cookie字符串，失败返回None
    """
    try:
        # 对密码进行MD5加密
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        
        login_url = "https://www.hifiti.com/user-login.htm"
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        }
        
        data = {
            "email": username,
            "password": password_md5
        }
        
        response = requests.post(
            url=login_url, 
            headers=headers, 
            data=data,
            timeout=15, 
            verify=False
        )
        
        response_text = response.text.strip()
        print(f"登录响应: {response_text}")
        
        # 检查登录是否成功
        if "登录成功" in response_text:
            # 提取cookie
            cookies = response.cookies
            bbs_token = None
            bbs_sid = None
            
            # 从响应头中提取cookie
            for cookie in cookies:
                if cookie.name == "bbs_token":
                    bbs_token = cookie.value
                elif cookie.name == "bbs_sid":
                    bbs_sid = cookie.value
            
            if bbs_token and bbs_sid:
                cookie_string = f"bbs_sid={bbs_sid}; bbs_token={bbs_token}"
                print(f"登录成功，获取到cookie: {cookie_string}")
                return cookie_string
            else:
                print("登录成功但无法提取cookie")
                return None
        else:
            print(f"登录失败: {response_text}")
            return None
            
    except Exception as e:
        print(f"登录过程中发生异常: {str(e)}")
        return None


def start(cookie):
    max_retries = 20
    retries = 0
    msg = ""
    while retries < max_retries:
        try:
            msg += "第{}次执行签到\n".format(str(retries + 1))
            sign_in_url = "https://www.hifiti.com/sg_sign.htm"
            headers = {
                "Cookie": cookie,
                "authority": "www.hifiti.com",
                "accept": "text/plain, */*; q=0.01",
                "accept-language": "zh-CN,zh;q=0.9",
                "origin": "https://www.hifiti.com",
                "referer": "https://www.hifiti.com/",
                "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            }

            rsp = requests.post(
                url=sign_in_url, headers=headers, timeout=15, verify=False
            )
            rsp_text = rsp.text.strip()
            print(rsp_text)
            success = False
            if "今天已经签过啦！" in rsp_text:
                msg += "已经签到过了，不再重复签到!\n"
                success = True
            elif "成功" in rsp_text:
                rsp_json = json.loads(rsp_text)
                msg += rsp_json["message"]
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
                msg += rsp_text + "\n"

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
            print("签到失败，失败原因:" + str(e))
            send("hifini 签到结果", str(e))
            retries += 1
            if retries >= max_retries:
                print("达到最大重试次数，签到失败。")
                break
            else:
                print("等待20秒后进行重试...")
                time.sleep(20)


if __name__ == "__main__":
    # 优先使用环境变量中的cookie
    cookie = os.getenv("HIFINI_COOKIE")
    username = None
    password = None

    
    # 如果没有cookie，尝试使用用户名密码登录
    if not cookie:
        if username and password:
            print("未找到cookie，尝试使用用户名密码登录...")
            cookie = login(username, password)
            if not cookie:
                print("登录失败，无法获取cookie")
                exit(1)
        else:
            print("请设置HIFINI_COOKIE环境变量，或者设置HIFINI_USERNAME和HIFINI_PASSWORD环境变量")
            exit(1)
    
    start(cookie)
