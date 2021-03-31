#!/usr/bin/python
# -*- coding: utf-8 -*-
import smtplib
import smbus
import time
import argparse
import getpass
import codecs
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate
from platform import python_version
from datetime import datetime


i2c = smbus.SMBus(1)
address = 0x48    

release = python_version()
if release > '2.6.2':
    from smtplib import SMTP_SSL
else:
    SMTP_SSL = None

def create_message(from_addr, sender_name, to_addr, subject, body, encoding):
    msg = MIMEText(body, 'plain', encoding)
    msg['Subject'] = Header(subject, encoding)
    form_jp = u"%s <%s>" % (str(Header(sender_name, encoding)), from_addr)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()
    return msg

def send_via_gmail(from_addr, to_addr, passwd, msg):
    if(temp > minTemp):
        if SMTP_SSL:
            print "send via SSL..."
            s = SMTP_SSL('smtp.gmail.com', 465)
            s.login(from_addr, passwd)
            s.sendmail(from_addr, [to_addr], msg.as_string())
            s.close()
            print 'mail sent!'
            time.sleep(600)
        else:
            print "send via TLS..."
            s = smtplib.SMTP('smtp.gmail.com', 587)
            if release < '2.6':
                s.ehlo()
            s.starttls()
            if release < '2.5':
                s.ehlo()
            s.login(from_addr, passwd)
            s.sendmail(from_addr, [to_addr], msg.as_string())
            s.close()
            print "mail sent!"
            time.sleep(600)

if __name__ == '__main__':

    minTemp = 23 #メールを送る最低温度の設定
    while True:
        block = i2c.read_i2c_block_data(address, 0x00, 12)
        temp = (block[0] << 8 | block[1]) >> 3
        if(temp >= 4096):
            temp -= 8192
        #print("Temperature:%6.2f" % (temp / 16.0))
        sensorTemp = (temp / 16.0)
        print('現在の温度は'+str(sensorTemp)+'度です。')
        time.sleep(10)
        hour = datetime.now().strftime('%H')
        minuet = datetime.now().strftime('%M')
        setTimer = hour + minuet
        if(setTimer == '0700' or setTimer == '1400' or setTimer '1800' or setTimer '2100'  ):
            print("I am working")
            parser = argparse.ArgumentParser(description='Send Gmail.')
            parser.add_argument('-t', '--to', dest='to_addr', type=str,
                                default='iamworkingwell@gmail.com',
                                help='To address') #警告メールの送信元のメールアドレス
            parser.add_argument('-s', '--subject', dest='subject', type=str,
                                default='「れいちゃん」冷凍庫監視システム', help='Title') #警告メールのタイトル
            parser.add_argument('-b', '--body', dest='body', type=str,
                                default='ご主人様、お疲れ様です。\n現在の冷凍庫の温度は'+str(sensorTemp)+'度です。\n冷凍庫が正常に動作しています。\n私はちゃんとお仕事してます、ご安心ください', help='Body of the mail.')
                                #警告メールのメール内容
            args = parser.parse_args()

            from_addr = "alert.from.rei@gmail.com" #警告メールの送信先（Gmail）
            sender_name=u'れいちゃん' #メールの送信者の名前
            print "from: %s <%s>" % (sender_name, from_addr)
            #passwd = getpass.getpass()
            passwd = 'Och0orr2' #警告元メールのパスワード（Gmail）
            to_addr = args.to_addr
            title = args.subject
            body = args.body
            msg = create_message(from_addr, sender_name, to_addr, title, body, 'utf-8')
            send_via_gmail(from_addr, to_addr, passwd, msg)
        if(sensorTemp > minTemp):
            parser = argparse.ArgumentParser(description='Send Gmail.')
            parser.add_argument('-t', '--to', dest='to_addr', type=str,
                                default='iamworkingwell@gmail.com',
                                help='To address') #警告メールの送信元のメールアドレス
            parser.add_argument('-s', '--subject', dest='subject', type=str,
                                default='！！警告！！「れいちゃん」冷凍庫監視システム', help='Title') #警告メールのタイトル
            parser.add_argument('-b', '--body', dest='body', type=str,
                                default='ご主人様大変ですっ。\n冷凍庫の温度が'+str(sensorTemp)+'度になったようです。\n冷凍庫が正常に動作しているか、直ちにご確認ください。', help='Body of the mail.')
                                #警告メールのメール内容
            args = parser.parse_args()

            from_addr = "iam@samuraibiz.jp" #警告メールの送信先（Gmail）
            sender_name=u'れいちゃん' #メールの送信者の名前
            print "from: %s <%s>" % (sender_name, from_addr)
            #passwd = getpass.getpass()
            passwd = 'uM-euK-Doup-' #警告元メールのパスワード（Gmail）
            to_addr = args.to_addr
            title = args.subject
            body = args.body
            msg = create_message(from_addr, sender_name, to_addr, title, body, 'utf-8')
            send_via_gmail(from_addr, to_addr, passwd, msg)
