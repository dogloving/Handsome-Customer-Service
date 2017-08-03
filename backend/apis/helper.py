#coding:utf-8
from django.core.mail import EmailMultiAlternatives
import time
from . import messages
 
def encrypt(key, string):   
    """
        字符串加密
    """
    bytearr = bytearray(str(string).encode('utf-8'))
    #求出 b 的字节数   
    length = len(bytearr)
    c = bytearray(length * 2)   
    j = 0   
    for i in range(0, length):   
        b1 = bytearr[i]
        b2 = b1 ^ key
        c1 = b2 % 16   
        c2 = b2 // 16
        c1 = c1 + 65   
        c2 = c2 + 65
        c[j] = c1 
        c[j + 1] = c2
        j = j + 2
    return c.decode('utf-8').lower()
 
def decrypt(key, string):
    """
        字符串解密
    """
    c = bytearray(str(string).upper().encode('utf-8'))   
    length = len(c)
    if length % 2 != 0:
        return ""
    length = length // 2
    bytearr = bytearray(length)
    j = 0
    for i in range(0, length):
        c1 = c[j]
        c2 = c[j + 1]
        j = j + 2
        c1 = c1 - 65
        c2 = c2 - 65
        b2 = c2 * 16 + c1
        b1 = b2 ^ key
        bytearr[i] = b1
    try:
        return bytearr.decode('utf-8')
    except:
        return ""

def get_active_code(email):
    """
        获取激活码
    """
    key = 9
    encry_str='%s|%s' % (email, time.strftime('%Y-%m-%d', time.localtime(time.time())))
    active_code = encrypt(key, encry_str)
    return active_code
 
def send_active_email(email, mySubject, myMessage):
    """
        发送邮件
    """
    subject = mySubject
    message = myMessage
 
    send_to = [email]
    #发送异常报错
    fail_silently = False
 
    msg = EmailMultiAlternatives(subject = subject, body = message, to = send_to)
    msg.attach_alternative(message, "text/html")
    msg.send(fail_silently)