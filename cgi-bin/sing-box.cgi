#!/usr/bin/perl
use strict;
use utf8;
use Encode qw(decode FB_CROAK);
use CGI::Carp qw(fatalsToBrowser carpout);

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %settings = ();
my %checked  = ();
my %selected = ();

# ====== 可调整路径 ======
my $service       = "/etc/init.d/sing-box";
my $singbox_bin   = "/usr/local/bin/sing-box";
my $singbox_conf  = "/usr/local/etc/sing-box/config.json";
my $singbox_log   = "/var/log/sing-box.log";
my $sudo_cmd      = "/usr/bin/sudo";
# ========================

&Header::getcgihash(\%settings);

# AJAX 日志接口
if ($settings{'ajax'} && $settings{'ajax'} eq 'log') {
    print "Content-Type: text/plain; charset=UTF-8\n\n";
    system("tail -n 100 $singbox_log");
    exit;
}

&Header::showhttpheaders();

my $action      = $settings{'ACTION'} || '';
my $cmd_output  = '';
my $show_output = 0;

sub decode_post_utf8 {
    my ($value) = @_;
    return '' unless defined $value;

    my $decoded = $value;
    eval {
        $decoded = decode('UTF-8', $value, FB_CROAK);
    };
    return $decoded;
}

sub run_service_command {
    my ($command) = @_;
    my $out = `$sudo_cmd -n $service $command 2>&1`;
    return normalize_command_output($out);
}

sub clear_log_file {
    my $out = `$sudo_cmd -n /bin/sh -c ': > $singbox_log' 2>&1`;
    return normalize_command_output($out);
}

sub normalize_command_output {
    my ($out) = @_;
    $out ||= '';
    return $out;
}

sub validate_config_text {
    my ($conf_text) = @_;

    my $tmp_dir  = "/tmp/singbox_check";
    my $tmp_conf = "$tmp_dir/config.json";
    my $tmp_src  = "/tmp/singbox_check_input.json";

    my $fh;
    if (!open($fh, ">:encoding(UTF-8)", $tmp_src)) {
        return (0, "无法创建临时配置文件");
    }
    print $fh $conf_text;
    close($fh);

    my $out = `$sudo_cmd -n /bin/sh -c 'rm -rf "$tmp_dir"; mkdir -p "$tmp_dir"; cp "$tmp_src" "$tmp_conf"' 2>&1`;
    my $code = $? >> 8;
    unlink $tmp_src;

    if ($code != 0) {
        return (0, normalize_command_output($out || "无法创建临时校验目录"));
    }

    $out = `$sudo_cmd -n $singbox_bin check -C $tmp_dir 2>&1`;
    $code = $? >> 8;

    `$sudo_cmd -n /bin/rm -rf $tmp_dir 2>&1`;

    if ($code == 0) {
        return (1, normalize_command_output($out));
    }

    return (0, normalize_command_output($out || "配置校验失败"));
}

 # ====== 保存配置 / 服务控制 ======
if ($action eq 'saveconf') {
    if (defined $settings{'CONF'}) {
        my $conf_text = decode_post_utf8($settings{'CONF'});

        my ($ok, $check_out) = validate_config_text($conf_text);
        if (!$ok) {
            $cmd_output  = "保存失败：配置校验未通过\n" . $check_out;
            $show_output = 1;
        } else {
            my $tmp_save = "/tmp/singbox_save_input.json";
            my $fh;
            if (!open($fh, ">:encoding(UTF-8)", $tmp_save)) {
                $cmd_output  = "保存失败：无法创建临时配置文件";
                $show_output = 1;
            } else {
                print $fh $conf_text;
                close($fh);

                my $out = `$sudo_cmd -n /bin/sh -c 'cp "$tmp_save" "$singbox_conf"' 2>&1`;
                my $code = $? >> 8;
                unlink $tmp_save;

                if ($code == 0) {
                    $cmd_output  = "配置已保存";
                    $show_output = 1;
                } else {
                    $cmd_output  = "保存失败：无法写入配置文件\n" . normalize_command_output($out);
                    $show_output = 1;
                }
            }
        }
    } else {
        $cmd_output  = "保存失败：未收到配置内容";
        $show_output = 1;
    }
}
elsif ($action eq 'start') {
    my $clear_out = clear_log_file();
    my $out = run_service_command('start');
    $cmd_output = ($clear_out ? $clear_out : '') . $out;
    $show_output = 1;
}
elsif ($action eq 'stop') {
    my $out = run_service_command('stop');
    $cmd_output = $out;
    $show_output = 1;
}
elsif ($action eq 'restart') {
    my $clear_out = clear_log_file();
    my $out = run_service_command('restart');
    $cmd_output = ($clear_out ? $clear_out : '') . $out;
    $show_output = 1;
}
elsif ($action eq 'clearlog') {
    my $out = clear_log_file();
    $cmd_output = ($out ? $out : '') . "日志已清空";
    $show_output = 1;
}

# ====== 状态检测 ======
my $status = run_service_command('status');
chomp $status;

# ====== 页面 ======
&Header::openpage("Sing-Box", 1, '');
print "<meta charset='UTF-8'>\n";
print <<'EOF';
<style>
.config-wrap {
    position: relative;
}
.config-editor {
    position: relative;
    background: #111;
    border: 1px solid #666;
    box-sizing: border-box;
    min-height: 420px;
}
.config-highlight {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    margin: 0;
    padding: 8px;
    overflow: auto;
    white-space: pre;
    overflow-wrap: normal;
    word-break: normal;
    font-family: monospace;
    font-size: 14px;
    line-height: 1.4;
    letter-spacing: normal;
    box-sizing: border-box;
    color: #ddd;
    pointer-events: none;
    tab-size: 4;
}
.editor-toolbar {
    margin-bottom: 8px;
}
.config-textarea {
    position: relative;
    z-index: 2;
    width: 100%;
    min-height: 420px;
    margin: 0;
    padding: 8px;
    border: 0;
    outline: none;
    resize: vertical;
    background: transparent;
    color: transparent;
    caret-color: #ffffff;
    font-family: monospace;
    font-size: 14px;
    line-height: 1.4;
    letter-spacing: normal;
    overflow: auto;
    tab-size: 4;
    box-sizing: border-box;
}
.config-textarea::selection {
    background: rgba(173, 216, 230, 0.35);
    color: transparent;
}
.status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}
.status-dot.running {
    background: #2ecc71;
}
.status-dot.stopped {
    background: #e74c3c;
}
.config-highlight .json-key {
    color: #79c0ff;
}
.config-highlight .json-string {
    color: #a5d6ff;
}
.config-highlight .json-number {
    color: #f2cc60;
}
.config-highlight .json-bool {
    color: #ff7b72;
}
.config-highlight .json-null {
    color: #ff7b72;
}
</style>
EOF
&Header::openbigbox('100%', 'left', '', '');

print "<form method='post'>";

# ====== 服务状态 ======
&Header::openbox('100%', 'left', '服务状态');

print "<b>状态:</b> ";
if ($status =~ /running/i) {
    print "<span class='status-dot running'></span><span style='color:green;'>运行中</span>";
} else {
    print "<span class='status-dot stopped'></span><span style='color:red;'>已停止</span>";
}

print "<br><br>";

print "<button type='submit' name='ACTION' value='start'>启动</button>  ";
print "<button type='submit' name='ACTION' value='stop'>停止</button>  ";
print "<button type='submit' name='ACTION' value='restart'>重启</button>";

if ($show_output) {
    print "<br><br><pre style='color:#ff3333;background:#111;padding:5px;box-sizing:border-box;margin:0;white-space:pre-wrap;'>";
    print &Header::escape($cmd_output);
    print "</pre>";
}

&Header::closebox();

# ====== 配置文件 ======
&Header::openbox('100%', 'left', '配置文件');

print "<div class='editor-toolbar'>";
print "<button type='submit' name='ACTION' value='saveconf'>保存配置</button>";
print "</div>";

my $conf_content = '';
if (-e $singbox_conf) {
    if (open(my $fh, "<:raw", $singbox_conf)) {
        local $/;
        $conf_content = <$fh>;
        close($fh);
        eval {
            $conf_content = decode('UTF-8', $conf_content, FB_CROAK);
        };
    } else {
        if (open(my $fh, "<", $singbox_conf)) {
            local $/;
            $conf_content = <$fh>;
            close($fh);
        }
    }
}

print "<div class='config-wrap'>";
print "<div class='config-editor'>";
print "<pre id='json-preview' class='config-highlight'></pre>";
print "<textarea id='conf-editor' class='config-textarea' name='CONF' wrap='off' oninput='updateJsonPreview()' onscroll='syncJsonScroll()' spellcheck='false'>";
print &Header::escape($conf_content);
print "</textarea>";
print "</div>";
print "</div>";

&Header::closebox();

# ====== 日志输出 ======
&Header::openbox('100%', 'left', '日志输出');

print "<div style='margin-bottom:8px;'><button type='submit' name='ACTION' value='clearlog'>清空日志</button></div>";

print "<pre id='logbox' style='background:#000;color:#0f0;height:220px;overflow:auto;width:100%;box-sizing:border-box;margin:0;white-space:pre-wrap;'>";

if (-e $singbox_log) {
    my @lines = `tail -n 100 $singbox_log`;
    print @lines;
} else {
    print "暂无日志文件。";
}

print "</pre>";

print <<'EOF';
<script>
(function() {
    var logbox = document.getElementById('logbox');
    if (logbox) {
        logbox.scrollTop = logbox.scrollHeight;
    }
})();
</script>
EOF

&Header::closebox();

print "</form>";

&Header::closebigbox();

print <<'EOF';
<script>
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

function highlightJson(text) {
    const escaped = escapeHtml(text);
    return escaped.replace(
        /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"\s*:?)|(\btrue\b|\bfalse\b)|(\bnull\b)|(-?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?)/g,
        function(match) {
            let cls = 'json-number';
            if (/^".*":$/.test(match)) {
                cls = 'json-key';
            } else if (/^"/.test(match)) {
                cls = 'json-string';
            } else if (/true|false/.test(match)) {
                cls = 'json-bool';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        }
    );
}

function updateJsonPreview() {
    var editor = document.getElementById('conf-editor');
    var preview = document.getElementById('json-preview');
    if (!editor || !preview) return;

    var text = editor.value;
    if (text.length === 0) {
        preview.innerHTML = '<br>';
    } else {
        preview.innerHTML = highlightJson(text) + '<span>\u200b</span>';
    }

    syncJsonScroll();
}

function syncJsonScroll() {
    var editor = document.getElementById('conf-editor');
    var preview = document.getElementById('json-preview');
    if (!editor || !preview) return;

    preview.scrollTop = editor.scrollTop;
    preview.scrollLeft = editor.scrollLeft;
}

window.addEventListener('DOMContentLoaded', function() {
    updateJsonPreview();
    syncJsonScroll();
});
</script>
EOF

&Header::closepage();