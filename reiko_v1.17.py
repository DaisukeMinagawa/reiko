#!/usr/bin/python
# -*- coding: utf-8 -*-
import smtplib
import smbus
import time
import argparse
import getpass
import codecs
import os
import math
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate
from platform import python_version
from datetime import datetime


i2c = smbus.SMBus(1)
address = 0x48

#i2c通信
def connectI2c():
    try:
        block = i2c.read_i2c_block_data(address, 0x00, 12)
        temp = (block[0] << 8 | block[1]) >> 3
        if(temp >= 4096):
            temp -= 8192
        return temp
    except:
        print 'i2c通信に失敗しました。温度計モジュールと配線を確認してください。'
        bool = 0
        return bool
        time.sleep(60)

#Pythonのバージョンが2.6.3以上だったらSMTP通信でメールを送信する
release = python_version()
if release > '2.6.2':
    from smtplib import SMTP_SSL
else:
    SMTP_SSL = None

#メールの雛形作成
def create_message(from_addr, sender_name, to_addr, subject, body, encoding):
    msg = MIMEText(body, 'plain', encoding)
    msg['Subject'] = Header(subject, encoding)
    form_jp = u"%s <%s>" % (str(Header(sender_name, encoding)), from_addr)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()
    return msg

#警告メールの送信
def send_alert_via_gmail(from_addr, to_addr, passwd, msg):
    if SMTP_SSL:
        print "send via SSL..."
    try:
        s = SMTP_SSL('smtp.gmail.com', 465)
        s.login(from_addr, passwd)
        s.sendmail(from_addr, [to_addr], msg.as_string())
        s.close()
        print 'mail sent!'
        print '一時的な問題かもしれないので10分停止します。'
        time.sleep(600) #一時的な温度上昇かもしれないので10分停止
    except:
        sound_email_alert()
        print 'SMTP_SSLでの送信に失敗しました。'
    else:
        print "send via TLS..."
    try:
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
            print '一時的な問題かもしれないので10分停止します。'
            time.sleep(600) #一時的な温度上昇かもしれないので10分停止 
    except:
        sound_email_alert()
        print 'SMTP_SSLTLSでの送信に失敗しました。'

#通常のメール送信
def send_via_gmail(from_addr, to_addr, passwd, msg):
    if SMTP_SSL:
        print "send via SSL..."
    try:
        s = SMTP_SSL('smtp.gmail.com', 465)
        s.login(from_addr, passwd)
        s.sendmail(from_addr, [to_addr], msg.as_string())
        s.close()
        print 'mail sent!'
        print '定時連絡が完了しました。'
    except:
        sound_email_alert()
        print 'SMTP_SSLでの送信に失敗しました。'
    else:
        print "send via TLS..."
    try:
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
            
            
    except:
        sound_email_alert()
        print 'SMTP_SSLTLSでの送信に失敗しました。'

#動作しているということの定時連絡
def working(setTime):
    if(setTime == '0800' or setTime == '1200' or setTime == '1600' or setTime == '2000'  ):
            print("I am working")
            sound_working(sensorTemp)
            parser = argparse.ArgumentParser(description='Send Gmail.')
            parser.add_argument('-t', '--to', dest='to_addr', type=str,
                                default='iamworkingwell@gmail.com',
                                help='To address') #警告メールの送信元のメールアドレス
            parser.add_argument('-s', '--subject', dest='subject', type=str,
                                default='「れいちゃん」冷凍庫監視システム', help='Title') #警告メールのタイトル
            parser.add_argument('-b', '--body', dest='body', type=str,
                                default='ご主人様、お疲れ様です。\n現在の冷凍庫の温度は'+str(sensorTemp)+'度です。\n私はちゃんとお仕事してます、ご安心ください', help='Body of the mail.')
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
            print '定時連絡が完了しました。'
            time.sleep(60) #定時連絡メールが連続して送られるのを防ぐため

#温度上昇の警告メール送信
def alert_temprature():
    if(sensorTemp >= minTemp):
            sound_temp_alert(sensorTemp)
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

            from_addr = "alert.from.rei@gmail.com" #警告メールの送信先（Gmail）
            sender_name=u'れいちゃん' #メールの送信者の名前
            print "from: %s <%s>" % (sender_name, from_addr)
            #passwd = getpass.getpass()
            passwd = 'Och0orr2' #警告元メールのパスワード（Gmail）
            to_addr = args.to_addr
            title = args.subject
            body = args.body
            msg = create_message(from_addr, sender_name, to_addr, title, body, 'utf-8')
            send_alert_via_gmail(from_addr, to_addr, passwd, msg)

#i2c通信に失敗した時の処理：モジュールか配線に問題がある
def alert_i2c():
    sound_i2c_alert()
    parser = argparse.ArgumentParser(description='Send Gmail.')
    parser.add_argument('-t', '--to', dest='to_addr', type=str,
                        default='iamworkingwell@gmail.com',
                        help='To address') #警告メールの送信元のメールアドレス
    parser.add_argument('-s', '--subject', dest='subject', type=str,
                        default='！！モジュールエラー！！「れいちゃん」冷凍庫監視システム', help='Title') #警告メールのタイトル
    parser.add_argument('-b', '--body', dest='body', type=str,
                        default='ご主人様申し訳ございません。\ni2c通信に失敗しました。\n株式会社合栄企画に連絡して、温度計モジュールと配線の修理を依頼をしてください。', help='Body of the mail.')
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
    send_alert_via_gmail(from_addr, to_addr, passwd, msg)

#ここから下は音声通知の設定
def sound_working(sensorTemp):
    message='ご主人様、お疲れ様です。現在の冷凍庫の温度は'+str(sensorTemp)+'度です。冷凍庫が正常に動作しています。私はちゃんとお仕事してます、ご安心ください'
    f = open('alert.txt', 'w')
    f.write(message)
    f.close()
    os.system('python rei_voice.py alert.txt')

def sound_temp_alert(sensorTemp):
    message='ご主人様大変です！冷凍庫の温度が'+str(sensorTemp)+'度になったようです。冷凍庫を確認してください。'
    f = open('alert.txt', 'w')
    f.write(message)
    f.close()
    os.system('python rei_voice.py alert.txt')
    
def sound_email_alert():
    message='ご主人様大変です！メール送信ができなくなっています。インターネット接続とメールサーバを確認してください。'
    f = open('alert.txt', 'w')
    f.write(message)
    f.close()
    os.system('python rei_voice.py alert.txt')

def sound_internet_alert():
    message='ご主人様大変です！インターネットに接続できません。インターネット接続を確認してください。'
    f = open('alert.txt', 'w')
    f.write(message)
    f.close()
    os.system('python rei_voice.py alert.txt')

def sound_i2c_alert():
    message='iツーc通信に失敗しました。株式会社ゴウエイ企画に連絡して、温度計モジュールと配線を確認の依頼をしてください。'
    f = open('alert.txt', 'w')
    f.write(message)
    f.close()
    os.system('python rei_voice.py alert.txt')
#ここまで

    
def get_current_time():
        hour = datetime.now().strftime('%H')
        minuet = datetime.now().strftime('%M')
        setTimer = hour + minuet
        return setTimer
    
if __name__ == '__main__':

    minTemp = 29 #メールを送る最低温度の設定
    while True:
        temp = connectI2c()
        if temp:
            #print("Temperature:%6.2f" % (temp / 16.0))
            sensorTemp = round((temp / 16.0),2)
            print('現在の温度は'+str(sensorTemp)+'度です。')
            time.sleep(10)
            setTime=get_current_time()
            working(setTime)
            alert_temprature()
        else:
            alert_i2c()
            
        
