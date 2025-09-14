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


def login_with_session(username, password, domain):
    """
    使用session方法登录HiFiNi网站
    :param username: 用户名
    :param password: 密码（明文，函数内部会进行MD5加密）
    :param domain: 网站域名
    :return: 登录成功返回session对象，失败返回None
    """
    try:
        # 创建session对象
        session = requests.Session()

        # 设置通用headers
        session.headers.update({
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        })

        # 首先访问首页
        print("正在访问首页...")
        home_url = f"https://{domain}/"
        home_response = session.get(home_url, timeout=15, verify=False)
        print(f"首页访问状态码: {home_response.status_code}")

        # 对密码进行MD5加密
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()

        # 登录
        print("正在尝试登录...")
        login_url = f"https://{domain}/user-login.htm"
        login_headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }

        data = {
            "email": username,
            "password": password_md5
        }

        response = session.post(
            url=login_url,
            headers=login_headers,
            data=data,
            timeout=15,
            verify=False
        )

        response_text = response.text.strip()
        print(f"登录响应: {response_text}")

        # 检查登录是否成功
        if "登录成功" in response_text:
            print("登录成功")
            return session
            # print("登录成功，正在验证登录状态...")

            # # 登录成功后再次访问首页验证
            # verify_response = session.get(home_url, timeout=15, verify=False)
            # verify_text = verify_response.text

            # # 检查首页是否包含用户名
            # if username in verify_text:
            #     print(f"登录验证成功！首页包含用户名 '{username}'")
            #     return session
            # else:
            #     print("登录验证失败，首页未找到用户名")
            #     return None
        else:
            print(f"登录失败: {response_text}")
            return None

    except Exception as e:
        print(f"登录过程中发生异常: {str(e)}")
        return None


def start(session, domain):
    max_retries = 20
    retries = 0
    msg = ""
    while retries < max_retries:
        try:
            msg += "第{}次执行签到\n".format(str(retries + 1))
            sign_in_url = f"https://{domain}/sg_sign.htm"
            headers = {
                "authority": domain,
                "accept": "text/plain, */*; q=0.01",
                "accept-language": "zh-CN,zh;q=0.9",
                "origin": f"https://{domain}",
                "referer": f"https://{domain}/",
                "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest",
            }

            rsp = session.post(
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
    login_list = os.getenv("HIFINI_LOGIN")
    if not login_list:
        print("请在脚本中设置cookies")
        exit(1)

    login_list = login_list.split("&")
    for login in login_list:
        domain, username, password = login.split("|")
        if not domain or not username or not password:
            print("登录信息不完整，无法执行签到")
            exit(1)
        print(f"正在为账户 {domain} {username} {password} 执行签到...")
        session = login_with_session(username, password, domain)
        if not session:
            print("登录失败，无法获取session")
            exit(1)
        start(session, domain)
        print("签到完成")

    # # 从环境变量获取配置
    # domain = os.getenv("HIFINI_DOMAIN", "www.hifiti.com")
    # username = os.getenv("HIFINI_USERNAME")
    # password = os.getenv("HIFINI_PASSWORD")

    # # 使用用户名密码登录
    # if username and password:
    #     print(f"正在使用用户名密码登录到 {domain}...")
    #     session = login_with_session(username, password, domain)
    #     if not session:
    #         print("登录失败，无法获取session")
    #         exit(1)
    # else:
    #     print("请设置HIFINI_USERNAME和HIFINI_PASSWORD环境变量")
    #     exit(1)

    # # 使用session进行签到
    # start(session, domain)
