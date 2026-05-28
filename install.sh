#!/bin/bash
set -e

print_step() {
    echo
    echo "==> $1"
}

if [[ $EUID -ne 0 ]]; then
    echo "错误：请使用 root 运行此脚本。" >&2
    exit 1
fi

print_step "准备安装 sing-box"
echo "该操作将安装 sing-box、Web 管理页面、菜单入口，并重载 Web 服务。"
read -p "是否继续？(y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "操作已取消。"
    exit 0
fi

print_step "检查安装目录"
for dir in ./menu ./cgi-bin ./etc ./bin; do
    if [[ ! -d "$dir" ]]; then
        echo "错误：缺少目录 $dir" >&2
        exit 1
    fi
done

print_step "复制文件"
install -d -m 755 /usr/local/etc/sing-box
cp -a ./menu/* /var/ipfire/menu.d/
cp -a ./cgi-bin/* /srv/web/ipfire/cgi-bin/
cp -a ./etc/init.d/sing-box /etc/init.d/sing-box
cp -a ./etc/sing-box/* /usr/local/etc/sing-box/
cp -a ./bin/* /usr/local/bin/

print_step "设置文件权限"
chmod +x /etc/init.d/sing-box
chmod +x /usr/local/bin/sing-box
chmod +x /srv/web/ipfire/cgi-bin/sing-box.cgi
chown root:nobody /usr/local/etc/sing-box/config.json
chmod 660 /usr/local/etc/sing-box/config.json

install -d -m 755 /var/run/sing-box
touch /var/log/sing-box.log
chown root:nobody /var/log/sing-box.log
chmod 664 /var/log/sing-box.log

print_step "配置开机自启"
ln -sf /etc/init.d/sing-box /etc/rc.d/rc3.d/S99sing-box

print_step "配置sudo权限"
sudoers_tmp="/etc/sudoers.d/sing-box.tmp"
{
    echo "nobody ALL=(ALL) NOPASSWD: /etc/init.d/sing-box"
} > "$sudoers_tmp"
chmod 440 "$sudoers_tmp"
visudo -cf "$sudoers_tmp" >/dev/null
mv "$sudoers_tmp" /etc/sudoers.d/sing-box

print_step "重载 Web 服务"
/etc/init.d/apache reload >/dev/null 2>&1

echo
echo "sing-box 安装完成！刷新页面，前往 Web 界面进行配置（服务 > Sing-Box）。"
