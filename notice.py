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

# 获取最新的修改
def get_latest_json_changes(file_path):
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
    added_contents = ''.join(added_lines)
    deadlines = re.findall('"deadline": "(.*?)"', added_contents)
    names = re.findall('"name": "(.*?)"', added_contents)
    institutes = re.findall('"institute": "(.*?)"', added_contents)
    websites = re.findall('"website": "(.*?)"', added_contents)

    # 生成结果
    result = ''
    for i,ddl in enumerate(deadlines):
        if ddl == '':
            ddl = 'N/A'
        else:
            try:
                ddl_new = datetime.fromisoformat(ddl)
                ddl_new = ddl_new.strftime('%Y-%m-%d %H:%M:%S')
                ddl = ddl_new
            except:
                print(f'日期错误: {names[i]}-{institutes[i]} {ddl}')
                pass
        result += f'{names[i]}-{institutes[i]} {ddl} {websites[i]}\n'
    print('\n\n', result)
    return result
        

if __name__ == '__main__':

    import os
    os.chdir('BoardCaster')

    content = get_latest_json_changes('data.json')

    # 发送邮件
    try:
        yag.send(
            to="baitime@foxmail.com",
            subject="预推免院校新增",
            contents=content,
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
