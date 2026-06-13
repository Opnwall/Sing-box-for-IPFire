#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"

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
for dir in "${SRC_DIR}/etc" "${SRC_DIR}/usr" "${SRC_DIR}/srv" "${SRC_DIR}/var"; do
    if [[ ! -d "$dir" ]]; then
        echo "错误：缺少目录 $dir" >&2
        exit 1
    fi
done

print_step "复制文件"
install -d -m 755 /etc/init.d
install -d -m 755 /usr/local/bin
install -d -m 755 /usr/local/etc/sing-box
install -d -m 755 /srv/web/ipfire/cgi-bin
install -d -m 755 /var/ipfire/menu.d
cp -a "${SRC_DIR}/etc/init.d/sing-box" /etc/init.d/sing-box
cp -a "${SRC_DIR}/usr/local/bin/sing-box" /usr/local/bin/sing-box
cp -a "${SRC_DIR}/usr/local/etc/sing-box/." /usr/local/etc/sing-box/
cp -a "${SRC_DIR}/srv/web/ipfire/cgi-bin/sing-box.cgi" /srv/web/ipfire/cgi-bin/sing-box.cgi
cp -a "${SRC_DIR}/var/ipfire/menu.d/81-singbox.menu" /var/ipfire/menu.d/81-singbox.menu

print_step "设置文件权限"
chmod +x /etc/init.d/sing-box
chmod +x /usr/local/bin/sing-box
chmod +x /srv/web/ipfire/cgi-bin/sing-box.cgi
if grep -q '"secret": "change-this-secret"' /usr/local/etc/sing-box/config.json; then
    singbox_secret="$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')"
    sed -i "s/\"secret\": \"change-this-secret\"/\"secret\": \"${singbox_secret}\"/" /usr/local/etc/sing-box/config.json
fi
chown root:nobody /usr/local/etc/sing-box/config.json
chmod 660 /usr/local/etc/sing-box/config.json

install -d -m 755 /var/run/sing-box
touch /var/log/sing-box.log
chown root:nobody /var/log/sing-box.log
chmod 664 /var/log/sing-box.log

print_step "配置开机自启"
ln -sf /etc/init.d/sing-box /etc/rc.d/rc3.d/S99sing-box

print_step "配置sudo权限"
sudoers_tmp="$(mktemp /tmp/sing-box-sudoers.XXXXXX)"
trap 'rm -f "$sudoers_tmp"' EXIT
cat > "$sudoers_tmp" <<'EOF'
nobody ALL=(root) NOPASSWD: /etc/init.d/sing-box start
nobody ALL=(root) NOPASSWD: /etc/init.d/sing-box stop
nobody ALL=(root) NOPASSWD: /etc/init.d/sing-box restart
nobody ALL=(root) NOPASSWD: /etc/init.d/sing-box status
EOF
chmod 440 "$sudoers_tmp"
visudo -cf "$sudoers_tmp" >/dev/null
mv "$sudoers_tmp" /etc/sudoers.d/sing-box
trap - EXIT

print_step "重载 Web 服务"
/etc/init.d/apache reload >/dev/null 2>&1

echo
echo "sing-box 安装完成！刷新页面，前往 Web 界面进行配置（服务 > Sing-Box）。"
