#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Digest 邮件发送脚本
用法: python send_email.py [日期，默认今天]
示例: python send_email.py 2026-06-30
"""

import smtplib
import sys
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# === 配置 ===
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER = "1821164461@qq.com"
RECEIVER = "1821164461@qq.com"
AUTH_CODE = "rogahqkqufeafabf"  # QQ邮箱SMTP授权码

BASE_DIR = Path(r"C:\Users\薛博文\Desktop\搜索信息\output")

def send_digest(date_str=None):
    """发送指定日期的 digest 到邮箱"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    data_file = BASE_DIR / date_str / "data.json"
    if not data_file.exists():
        print("[FAIL] Data file not found: " + str(data_file))
        sys.exit(1)

    # 读取数据
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    stats = data["stats"]
    total = stats["total"]

    # 生成 HTML 邮件内容
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; max-width: 600px; margin: 0 auto; padding: 16px; background: #f5f5f5;">
  <div style="background: linear-gradient(135deg, #2563eb, #7c3aed); color: #fff; padding: 24px; border-radius: 12px 12px 0 0; text-align: center;">
    <h1 style="margin:0; font-size: 22px;">📰 Daily Digest</h1>
    <p style="margin:8px 0 0; opacity:0.85; font-size:14px;">{date_str} · {total} 条信息</p>
  </div>

  <div style="background: #fff; padding: 16px; border-radius: 0 0 12px 12px;">
    <div style="margin-bottom: 20px;">
      <a href="https://xbw247.github.io/newsdigest/" style="display: inline-block; background: #2563eb; color: #fff; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-size: 15px;">📱 在浏览器中查看完整版</a>
    </div>

    <h2 style="font-size: 17px; margin: 16px 0 8px;">📊 今日概览</h2>
    <table style="width:100%; border-collapse:collapse; font-size: 13px; margin-bottom: 16px;">
      <tr><td style="padding:6px 8px; border-bottom:1px solid #eee;">📋 信息源</td><td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:right; font-weight:600;">{len(stats['by_source'])}</td></tr>
      <tr><td style="padding:6px 8px; border-bottom:1px solid #eee;">🏷️ 分类</td><td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:right; font-weight:600;">{len(stats['by_category'])}</td></tr>
      <tr><td style="padding:6px 8px;">📰 文章数</td><td style="padding:6px 8px; text-align:right; font-weight:600;">{total}</td></tr>
    </table>

    <h2 style="font-size: 17px; margin: 16px 0 8px;">🔥 热门分类 TOP 8</h2>
    <table style="width:100%; border-collapse:collapse; font-size: 13px;">
"""
    # 按数量排序分类
    top_cats = sorted(stats["by_category"].items(), key=lambda x: x[1], reverse=True)[:8]
    for cat, count in top_cats:
        html += f'      <tr><td style="padding:5px 8px; border-bottom:1px solid #f0f0f0;">{cat}</td><td style="padding:5px 8px; border-bottom:1px solid #f0f0f0; text-align:right; font-weight:600;">{count}</td></tr>\n'

    html += """
    </table>

    <h2 style="font-size: 17px; margin: 16px 0 8px;">⭐ 高分推荐 (quality_score=5)</h2>
"""

    # 提取所有 5 分文章
    top_items = []
    for cat, items in data.get("categorized", {}).items():
        for item in items:
            if item.get("quality_score") == 5:
                top_items.append(item)

    # 按 score 排序
    top_items.sort(key=lambda x: x.get("score", 0), reverse=True)

    for i, item in enumerate(top_items[:20]):
        title = item["title"][:80] + ("…" if len(item["title"]) > 80 else "")
        summary = item.get("summary", "")[:100]
        html += f"""
      <div style="border-left: 3px solid #2563eb; padding: 6px 12px; margin-bottom: 8px;">
        <a href="{item['url']}" style="text-decoration: none; color: #1a1a2e; font-weight: 600; font-size: 13px;">{title}</a>
        <div style="font-size: 11px; color: #6b7280; margin-top: 2px;">{item['emoji']} {item['category']} · {item['source']} · ★★★★★</div>
        <div style="font-size: 12px; color: #4b5563; margin-top: 2px;">{summary}</div>
      </div>"""

    html += f"""
    <div style="text-align: center; margin-top: 20px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
      <p style="font-size: 12px; color: #9ca3af;">共 {total} 条信息，以上为高分精选</p>
      <a href="https://xbw247.github.io/newsdigest/" style="color: #2563eb; font-size: 13px;">📱 点击查看完整 Digest（适配手机）</a>
    </div>
  </div>
</body>
</html>
"""

    # 纯文本备用
    plain_text = f"""Daily Digest - {date_str}

今日收集 {total} 条信息，涵盖 {len(stats['by_category'])} 个分类。

高分推荐:
{chr(10).join([f"  ★ {item['emoji']} [{item['category']}] {item['title'][:80]} — {item.get('summary', '')[:80]}" for item in top_items[:10]])}

完整版请查看: https://xbw247.github.io/newsdigest/
"""

    # 构建邮件
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📰 Daily Digest - {date_str} ({total}条)"
    msg["From"] = SENDER
    msg["To"] = RECEIVER

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER, AUTH_CODE)
        server.sendmail(SENDER, [RECEIVER], msg.as_string())
        server.quit()
        print("[OK] Email sent successfully! " + date_str + " -> " + RECEIVER)
        print("   " + str(total) + " items, " + str(len(top_items)) + " highlights")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[FAIL] SMTP auth failed! Please check authorization code.")
        return False
    except Exception as e:
        print("[FAIL] Send error: " + str(e))
        return False


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    send_digest(date_arg)
