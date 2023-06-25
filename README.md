# hifini_sign_in
hifini - 音乐磁场 青龙自动签到脚本

## 使用
```shell
ql repo https://github.com/fengwenhua/hifini_sign_in.git "hifini.py" "" "sendNotify"
```

国内机器如下：

```shell
ql repo https://ghproxy.com/https://github.com/fengwenhua/hifini_sign_in.git "hifini.py" "" "sendNotify"
```

青龙面板新增环境变量: `HIFINI_COOKIE`

值应该类似如下:

```
bbs_sid=9rj8t4fublupqxxxxxxxx; Hm_lvt_4ab5ca5f7xxxxxxxx=168xxxxxxxx; bbs_token=7txxxxxxxx; Hm_lpvt_4ab5ca5f7f036f4a4747fxxxxxxxx2=168xxxxxxxx
```
