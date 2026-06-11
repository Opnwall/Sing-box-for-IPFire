## Sing-box for IPFire

![IPFire](https://img.shields.io/badge/IPFire-2.29-orange)
![Architecture](https://img.shields.io/badge/Arch-x86__64-blue)
![Sing-Box](https://img.shields.io/badge/Sing--Box-Latest-brightgreen)
![License](https://img.shields.io/badge/License-GPLv3--orange)

控制 sing-box 运行，实现透明代理。包含配置修改、程序控制、日志查看功能。在IPFire-2.29-x86_64-Core-Update-200
上测试通过。

![](image/sing-box.png)

## 集成程序
[sing-box](https://github.com/SagerNet/sing-box/releases)

## 注意事项
1. 当前仅支持x86_64 平台。
2. 脚本集成了可用的默认设置，参照修改节点信息即可使用。
3. 为减少长期运行保存的日志数量，在调试完成后，请将所有配置的日志类型修改为error或warn。

## 安装命令
以 root 用户登录终端，运行以下命令安装：
```bash
sh install.sh
```
## 卸载命令
以 root 用户登录终端，运行以下命令卸载：
```bash
sh uninstall.sh
```

## 配置过程
1. 安装完成，导航到 服务>Sing-Box 菜单，修改配置并保存。
2. 点击启动按钮，根据输出的日志内容，排除配置文件错误。
3. 正常启动后，客户端访问 ip111.cn，检查分流是否正常。

## 其他事项
1. 脚本具备开机自启功能。
2. 默认配置文件开启了 api 功能，访问 http://lan_ip:9090/ui 登录仪表盘。
