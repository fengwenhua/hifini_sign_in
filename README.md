# hifini_sign_in
hifini - 音乐磁场 青龙自动签到脚本

* 支持多用户
* 支持多站点

测试适用于 https://www.hifiti.com ，其他类似的hifi站点应该也行，如果不行，可以提一个issuse反馈一下

## 使用
```shell
ql repo https://github.com/fengwenhua/hifini_sign_in.git "hifini.py" "" "sendNotify"
```

国内机器如下：

```shell
ql repo https://gitproxy.fengwenhuaimg.top/https://github.com/fengwenhua/hifini_sign_in.git "hifini.py" "" "sendNotify"
```

青龙面板新增环境变量: `HIFINI_LOGIN`

值由三部分组成，用`|`分割：

```
域名|用户名|密码
```

值应该类似如下:

```
www.hifiti.com|zhangsan|password123456
```
