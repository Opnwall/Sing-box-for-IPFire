## Sing-box for IPFire

![IPFire](https://img.shields.io/badge/IPFire-2.29-orange)
![Architecture](https://img.shields.io/badge/Arch-x86__64-blue)
![Sing-Box](https://img.shields.io/badge/Sing--Box-Latest-brightgreen)
![License](https://img.shields.io/badge/License-GPLv3-green)

sing-box 是一款功能强大、性能优秀的开源网络代理平台，支持多种主流代理协议，包括 Shadowsocks、VMess、VLESS、Trojan、Hysteria、TUIC 和 SOCKS 等。

它基于现代化架构设计，具备高性能、低资源占用和灵活配置等特点，可用于网络代理、流量分流、负载均衡以及安全访问等场景。sing-box 同时支持 Linux、Windows、macOS、Android 和 iOS 等多个平台，并兼容 TUN 模式、DNS 规则和丰富的路由策略。

由于其强大的功能和活跃的社区支持，sing-box 已成为许多用户构建自托管网络代理和跨平台网络解决方案的重要工具之一。

本插件可以在 IPFire 上控制 sing-box 运行，实现透明代理。包含配置修改、程序控制、日志查看功能。

在IPFire-2.29-x86_64-Core-Update-203上测试通过。

![](image/sing-box.png)

## 集成程序
[sing-box](https://github.com/SagerNet/sing-box/releases)

## 注意事项
1. 当前仅支持x86_64 平台。
2. 脚本集成了可用的默认设置，参照修改节点信息即可使用。
3. 为减少长期运行保存的日志数量，在调试完成后，请将日志层级修改为error。

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

## 免责声明
非官方插件，不受IPFire团队支持，一切后果由使用者自负。
