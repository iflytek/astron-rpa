import ast
import smtplib
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

import requests
from astronverse.scheduler.error import (
    BizException,
    EMAIL_LOGIN_ERROR,
    EMAIL_SEND_ERROR,
    SMS_SEND_ERROR,
    SMS_SEND_ERROR_FORMAT,
)
from astronverse.scheduler.utils.utils import get_settings


class NotifyUtils:
    def __init__(self, svc):
        self.svc = svc
        self.settings = get_settings()
        self.email_setting = self.settings.get("msgNotifyForm", {}).get("email", {})
        self.msg_setting = self.settings.get("msgNotifyForm", {}).get("phone_msg", {})
        self.email_msg = None
        self.mail_handler = None

    @staticmethod
    def parse_cc(cc_str):
        """
        解析抄送地址，支持英文/中文分号分隔的单行字符串。
        """
        if not cc_str:
            return []
        # 统一分隔符为英文分号
        cc_str = str(cc_str).replace("；", ";")
        return [item for item in cc_str.split(";") if item]

    @staticmethod
    def format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, "utf-8").encode(), addr))

    def login_send(self):
        if self.email_setting.get("is_default", True):
            return
        mail_server = self.email_setting["mail_server"]
        mail_port = self.email_setting["mail_port"]
        sender_mail = self.email_setting["sender_mail"]
        password = self.email_setting["password"]
        use_ssl = self.email_setting["use_ssl"]
        self.email_msg = MIMEMultipart()
        if use_ssl:
            self.mail_handler = smtplib.SMTP_SSL(mail_server, int(mail_port), timeout=20)
        else:
            self.mail_handler = smtplib.SMTP(mail_server, int(mail_port), timeout=20)
        try:
            self.mail_handler.login(sender_mail, password)
        except smtplib.SMTPException as e:
            raise BizException(EMAIL_LOGIN_ERROR, "发送异常邮件登陆失败！{}".format(e))

    def send(self, robot_name, run_time):
        if self.email_setting.get("is_enable", False):
            content = "【讯飞星火RPA】您运行的机器人 {}于{}运行失败，请您及时查看".format(robot_name, run_time)
            self.login_send()
            self.send_email(content)
        if self.msg_setting.get("is_enable", False):
            self.send_sms(robot_name, run_time)

    def send_email(self, content: str = "机器人运行出错，请检查！"):
        # receiver 只支持单人
        receiver = str(self.email_setting.get("receiver", "")).strip()
        # cc 支持英文/中文分号分隔
        cc_raw = self.email_setting.get("cc", "")
        cc_list = self.parse_cc(cc_raw)
        if self.email_setting.get("is_default", True):
            try:
                data = {
                    "subject": "RPA机器人运行异常通知",
                    "content": content,
                    "receiver": receiver,
                    "cc": ";".join(cc_list),
                }
                response = requests.post(
                    "http://127.0.0.1:{}/api/robot/mail/send".format(self.svc.rpa_route_port),
                    json=data,
                )
                status_code = response.status_code
                text = response.text
                if status_code != 200:
                    raise BizException(EMAIL_SEND_ERROR, "发送异常邮件发送失败 {}".format(text))
            except Exception as e:
                raise BizException(EMAIL_SEND_ERROR, "发送异常邮件发送失败！{}".format(e))
        else:
            sender_mail = self.email_setting["sender_mail"]
            try:
                self.email_msg = MIMEMultipart()
                self.email_msg["From"] = self.format_addr(f"星辰RPA <{sender_mail}>")
                self.email_msg["To"] = Header(receiver)
                self.email_msg["Cc"] = ";".join(cc_list)
                self.email_msg["date"] = time.strftime("%a, %d %b %Y %H:%M:%S %z")
                self.email_msg["Subject"] = "RPA机器人运行异常通知"
                self.email_msg.attach(MIMEText(content, "plain", "utf-8"))
                # 开始发送
                recipients = [receiver] + cc_list
                self.mail_handler.sendmail(
                    sender_mail,
                    recipients,
                    self.email_msg.as_string(),
                )
            except Exception as e:
                raise BizException(EMAIL_SEND_ERROR, "发送异常邮件发送失败！{}".format(e))

    def send_sms(self, robot_name, run_time):
        try:
            params = {
                "phone": self.msg_setting["receiver"],
                "robotName": robot_name,
                "errorTime": run_time,
            }
            response = requests.get(
                "http://127.0.0.1:{}/api/robot/sms/sendForRobotError".format(self.svc.rpa_route_port),
                params=params,
            )
            status_code = response.status_code
            text = response.text
            if status_code != 200:
                raise BizException(SMS_SEND_ERROR_FORMAT.format(text), f"发送短信接口调用失败！{text}")
        except Exception as e:
            raise BizException(SMS_SEND_ERROR, "发送短信接口调用失败！")