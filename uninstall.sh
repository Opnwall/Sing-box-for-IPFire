#!/bin/bash
# sing-box 卸载脚本
set -e

print_step() {
    echo
    echo "==> $1"
}

if [[ $EUID -ne 0 ]]; then
    echo "错误：请使用 root 运行此脚本。" >&2
    exit 1
fi

print_step "准备卸载 sing-box"
echo "该操作将删除 sing-box 程序、Web 管理页面、启动项、运行文件和配置文件。"
read -p "是否继续？(y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "操作已取消。"
    exit 0
fi

print_step "停止 sing-box 服务"
/etc/init.d/sing-box stop >/dev/null 2>&1 || true

print_step "移除开机自启"
rm -f /etc/rc.d/rc3.d/S99sing-box

print_step "删除程序文件"
rm -f /etc/init.d/sing-box
rm -f /usr/local/bin/sing-box
rm -f /srv/web/ipfire/cgi-bin/sing-box.cgi
rm -f /etc/sudoers.d/sing-box

print_step "删除运行文件"
rm -rf /var/run/sing-box
rm -f /var/log/sing-box.log

print_step "删除配置文件"
rm -rf /usr/local/etc/sing-box
rm -f /var/ipfire/menu.d/81-singbox.menu

print_step "重载 Web 服务"
/etc/init.d/apache reload >/dev/null 2>&1

echo
echo "sing-box 卸载完成！"