import smtplib

from email import encoders

from email.header import Header

from email.mime.text import MIMEText

from email.utils import parseaddr, formataddr


def send_email(from_addr, to_addr, subject, password):
    msg = MIMEText("邮件正文", 'html', 'utf-8')

    msg['From'] = u'<%s>' % from_addr

    msg['To'] = u'<%s>' % to_addr

    msg['Subject'] = subject

    smtp = smtplib.SMTP_SSL('smtp.163.com', 465)

    smtp.set_debuglevel(1)

    smtp.ehlo("smtp.163.com")

    smtp.login(from_addr, password)

    smtp.sendmail(from_addr, [to_addr], msg.as_string())


if __name__ == "__main__":
    # 这里的密码是开启smtp服务时输入的客户端登录授权码，并不是邮箱密码

    # 现在很多邮箱都需要先开启smtp才能这样发送邮件

    send_email(u"from_addr", u"to_addr", u"主题", u"password")
