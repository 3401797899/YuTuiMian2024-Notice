import yagmail
import subprocess
import re
import os
from datetime import datetime

# 邮箱设置
sender_email = os.environ['FROM_MAIL']
sender_password = os.environ['FROM_MAIL_PWD']

# 创建 yagmail 客户端
yag = yagmail.SMTP(sender_email, sender_password, host='smtp.qq.com', port=465)

def create_html_table(names, institutes, deadlines, websites):
    html = """
   <html>
    <body>
    <table style="border-collapse: collapse;">
        <tr>
            <th style="border: 1px solid black;padding: 8px;text-align: left;">院校</th>
            <th style="border: 1px solid black;padding: 8px;text-align: left;">截至时间</th>
            <th style="border: 1px solid black;padding: 8px;text-align: left;">网址</th>
        </tr>
    """

    for i, ddl in enumerate(deadlines):
        if ddl == '':
            ddl = 'N/A'
        else:
            try:
                ddl_new = datetime.fromisoformat(ddl)
                ddl = ddl_new.strftime('%Y-%m-%d %H:%M:%S')
            except:
                print(f'日期错误: {names[i]}-{institutes[i]} {ddl}')

        html += f"""
        <tr>
            <td style="border: 1px solid black;padding: 8px;text-align: left;">{names[i]}-{institutes[i]}</td>
            <td style="border: 1px solid black;padding: 8px;text-align: left;">{ddl}</td>
            <td style="border: 1px solid black;padding: 8px;text-align: left;"><a href="{websites[i]}">{websites[i]}</a></td>
        </tr>
        """

    html += """
    </table>
    </body>
    </html>
    """

    return html

# 获取最新的修改
def get_added_content(file_path):
    # 执行 git diff 命令获取最新 commit 的变动
    result = subprocess.run(
        ['git', 'diff', 'HEAD~1..HEAD', '--', file_path],
        capture_output=True,
        text=True,
        check=True
    )
    
    # 解析输出
    lines = result.stdout.split('\n')
    added_lines = [line[1:] for line in lines if line.startswith('+') and not line.startswith('+++')]
    return ''.join(added_lines)
    
def generate_json_changes(added_contents):
    deadlines = re.findall('"deadline": "(.*?)"', added_contents)
    names = re.findall('"name": "(.*?)"', added_contents)
    institutes = re.findall('"institute": "(.*?)"', added_contents)
    websites = re.findall('"website": "(.*?)"', added_contents)

    # 生成结果
    result = create_html_table(names, institutes, deadlines, websites)
    return result

def generate_readme_changes(added_contents):
    # 生成结果
    result = re.findall('【报名截止：(.*?)】 \[(.*?)\]\((.*?)\)',added_contents)
    print(result[0])
    return result

if __name__ == '__main__':

    json_content = get_added_content('data.json')
    content = generate_json_changes(json_content)
    readme_content = get_added_content('README.md')
    generate_readme_changes(readme_content)

    # 发送邮件
    try:
        yag.send(
            to=["baitime@foxmail.com","1328273623@qq.com"],
            subject="预推免院校新增 -- 来自BoardCaster数据库",
            contents=content.replace('\n','')
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
