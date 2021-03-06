# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 13:54:18 2018

@author: Sherlock Holmes
"""

from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import hashlib
from Crypto.Cipher import AES
import array
import os

seed = '1234567890123456'

# 固定计数器（非常不安全！）
# counter = os.urandom(16)

class Secret(object):
  def __init__(self, secret=None):
    if secret is None: secret = os.urandom(16)
    self.secret = secret
    self.reset()
  def counter(self):
    for i, c in enumerate(self.current):
      self.current[i] = c + 1
      if self.current: break
    return self.current.tostring()
  def reset(self):
    self.current = array.array('B', self.secret)

secret = Secret()

# 口令hash返回16字节str
def hash_16B(password):
    md5 = hashlib.md5()
    md5.update(password)
    return md5.hexdigest()

# ECB模式初始化AES
def init_ECB(password):
    return AES.new(hash_16B(password), AES.MODE_ECB)

# CBC模式初始化AES
def init_CBC(password):
    return AES.new(hash_16B(password), AES.MODE_CBC, seed)

# CFB模式初始化AES
def init_CFB(password):
    return AES.new(hash_16B(password), AES.MODE_CFB, seed)

# OFB模式初始化AES
def init_OFB(password):
    return AES.new(hash_16B(password), AES.MODE_OFB, seed)

# CTR模式初始化AES
def init_CTR(password):
    #return AES.new(hash_16B(password), AES.MODE_CTR, counter=lambda:counter)
    return AES.new(hash_16B(password), AES.MODE_CTR, counter=secret.counter)

# 模式字典
modeDict = {
        'ECB': init_ECB,
        'CBC': init_CBC,
        'CFB': init_CFB,
        'OFB': init_OFB,
        'CTR': init_CTR
        }

# AES加密
def encrypt_AES(text, password, mode):
    # 填充分组，使用PKCS7Padding填充方式, 确保其长度为16的整数倍
    # CFB模式不需要填充
    if mode != 'CFB':
        for i in range(0, (16 - text.__len__() % 16) % 16):
            text += b'\0'
    AESCipher = modeDict[mode](password)
    return AESCipher.encrypt(text)

# AES解密
def decrypt_AES(cipher, password, mode):
    AESCipher = modeDict[mode](password)
    return AESCipher.decrypt(cipher)

# 通过文件输入明文和口令，将结果输出到一个文件
def encrypt_AES_file(textPath, passwordPath, cipherPath, Emode):
    try:
        textFile = open(textPath, mode = 'rb')
    except IOError:
        # 明文文件路径错误
        return 1
    try:
        passwordFile = open(passwordPath, mode = 'rb')
    except IOError:
        # 口令文件路径错误
        return 2
    try:
        cipherFile = open(cipherPath, mode = 'wb')
    except IOError:
        # 密文文件路径错误
        return 3
    cipherFile.write( encrypt_AES(textFile.read(), passwordFile.read(), Emode) )
    textFile.close()
    passwordFile.close()
    cipherFile.close()
    return 0

# 通过文件输入密文和口令，将恢复的明文输出到一个文件
def decrypt_AES_file(cipherPath, passwordPath, textPath, Dmode):
    try:
        cipherFile = open(cipherPath, mode = 'rb')
    except IOError:
        # 密文文件路径错误
        return 1
    try:
        passwordFile = open(passwordPath, mode = 'rb')
    except IOError:
        # 口令文件路径错误
        return 2
    try:
        textFile = open(textPath, mode = 'wb')
    except IOError:
        # 明文文件路径错误
        return 3    
    textFile.write( decrypt_AES(cipherFile.read(), passwordFile.read(), Dmode) )
    cipherFile.close()
    passwordFile.close()
    textFile.close()
    return 0

# 打开窗口中要插入的图片文件
tmp = Tk()
img1 = PhotoImage(file='encrypt.png')
img2 = PhotoImage(file='decrypt.png')


# 程序图形化窗体类
class GraphicInterface(Frame):
    # 构造函数
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
    # 创建窗体的函数
    def createWidgets(self):
        # 使用ttk中的Notebook作为窗体的模板
        self.nb = ttk.Notebook()
        # 窗体标题
        self.master.title('AES加密解密程序V3.0')
        # 设置窗体的几何大小
        self.master.geometry('800x400')
        # 设置窗体的左上角的图标
        self.master.iconbitmap('aes.ico')
        
        # 初始化明文、密文、加密密钥、解密密钥文件路径为空（便于后面的异常处理）
        self.filename1 = ""
        self.filename2 = ""
        self.filename3 = ""
        self.filename4 = ""
        
        # 向Notebook窗体中添加组件
        
        # “加密”选项卡
        self.page1 = ttk.Frame(self.nb)
        # “加密”页图片
        self.image1 = Label(self.page1, image=img1)
        self.image1.pack(side=LEFT, fill=Y, padx=10, pady=10)
        # 提示文本
        self.label1 = Label(self.page1, text="请选择要加密的文本")
        self.label1.pack(side=TOP, fill=BOTH, padx=5, pady=5)
        self.label2 = Label(self.page1, text="明文文本路径：")
        self.label2.pack(padx=5, pady=5)
        # 显示明文文件路径的文本
        self.txt1 = Text(self.page1, height=1, width=50)
        self.txt1.pack(padx=5, pady=5)
        # 选择文件的按钮
        self.fileChooser1 = Button(self.page1, text='选择文件', command=self.selectPlainText)
        self.fileChooser1.pack(padx=5, pady=5)
        # 提示文本
        self.label3 = Label(self.page1, text="密钥文本路径：")
        self.label3.pack(padx=5, pady=5)
        # 显示加密密钥文件路径的文本
        self.txt2 = Text(self.page1, height=1, width=50)
        self.txt2.pack(padx=5, pady=5)
        # 选择文件的按钮
        self.fileChooser2 = Button(self.page1, text='选择文件', command=self.selectPassword1)
        self.fileChooser2.pack(padx=5, pady=5)
        # 提示文本
        self.label4 = Label(self.page1, text="请选择加密方式：")
        self.label4.pack(padx=5, pady=5)
        # 加密模式下拉框
        self.comboList1 = ['ECB模式','CBC模式','CFB模式','OFB模式','CTR模式']
        self.combobox1 = ttk.Combobox(self.page1, values=self.comboList1)
        self.combobox1.pack(padx=5, pady=5)
        # 开始加密按钮
        self.alertButton1 = Button(self.page1, text='开始加密', command=self.encrypt)
        self.alertButton1.pack(side=BOTTOM, padx=5, pady=10)
        
        # “解密”选项卡
        self.page2 = ttk.Frame(self.nb)
        # “解密”页图片
        self.image2 = Label(self.page2, image=img2)
        self.image2.pack(side=LEFT, fill=Y, padx=10, pady=10)
        # 提示文本
        self.label5 = Label(self.page2, text="请选择要解密的文本")
        self.label5.pack(side=TOP, fill=BOTH, padx=5, pady=5)
        self.label6 = Label(self.page2, text="密文文本路径：")
        self.label6.pack(padx=5, pady=5)
        # 显示密文文件路径的文本
        self.txt3 = Text(self.page2, height=1, width=60)
        self.txt3.pack(padx=5, pady=5)
        # 选择文件的按钮
        self.fileChooser3 = Button(self.page2, text='选择文件', command=self.selectCipherText)
        self.fileChooser3.pack(padx=5, pady=5)
        # 提示文本
        self.label7 = Label(self.page2, text="密钥文本路径：")
        self.label7.pack(padx=5, pady=5)
        # 显示解密密钥文件路径的文本
        self.txt4 = Text(self.page2, height=1, width=60)
        self.txt4.pack(padx=5, pady=5)
        # 选择文件的按钮
        self.fileChooser4 = Button(self.page2, text='选择文件', command=self.selectPassword2)
        self.fileChooser4.pack(padx=5, pady=5)
        # 提示文本
        self.label8 = Label(self.page2, text="请选择解密方式：")
        self.label8.pack(padx=5, pady=5)
        # 解密模式下拉框
        self.comboList2 = ['ECB模式','CBC模式','CFB模式','OFB模式','CTR模式']
        self.combobox2 = ttk.Combobox(self.page2, values=self.comboList2)
        self.combobox2.pack(padx=5, pady=5)
        # 开始解密按钮
        self.alertButton2 = Button(self.page2, text='开始解密', command=self.decrypt)
        self.alertButton2.pack(side=BOTTOM, padx=5, pady=10)
        
        # 将两个选项卡页面加入窗体
        self.nb.add(self.page1, text='加密')
        self.nb.add(self.page2, text='解密')
        self.nb.pack(expand=1, fill="both")
    
    # 选择明文文件函数（限定txt文本）
    def selectPlainText(self):
        self.filename1 = tk.filedialog.askopenfilename(filetypes=[("文本格式","txt")])
        self.txt1.delete(1.0, END)
        self.txt1.insert(1.0, self.filename1)
    
    # 选择加密密钥文件函数（限定txt文本）
    def selectPassword1(self):
        self.filename2 = tk.filedialog.askopenfilename(filetypes=[("文本格式","txt")])
        self.txt2.delete(1.0, END)
        self.txt2.insert(1.0, self.filename2)
    
    # 选择密文文件函数（限定txt文本）
    def selectCipherText(self):
        self.filename3 = tk.filedialog.askopenfilename(filetypes=[("文本格式","txt")])
        self.txt3.delete(1.0, END)
        self.txt3.insert(1.0, self.filename3)
    
    # 选择解密密钥文件函数（限定txt文本）
    def selectPassword2(self):
        self.filename4 = tk.filedialog.askopenfilename(filetypes=[("文本格式","txt")])
        self.txt4.delete(1.0, END)
        self.txt4.insert(1.0, self.filename4)

    # 加密函数（含异常处理）
    def encrypt(self):
        # 明文文本路径为空，报错
        if self.filename1 == "":
            messagebox.showinfo('Message', '您还未选择明文文本！')
        # 加密密钥文本路径为空，报错
        elif self.filename2 == "":
            messagebox.showinfo('Message', '您还未选择密钥文本！')
        else:
            mode = self.combobox1.get()
            if mode == 'ECB模式':
                encrypt_AES_file(self.filename1, self.filename2, "ciphertext.txt", 'ECB')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under ECB Mode!')
            elif mode == 'CBC模式':
                encrypt_AES_file(self.filename1, self.filename2, "ciphertext.txt", 'CBC')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under CBC Mode!')
            elif mode == 'CFB模式':
                encrypt_AES_file(self.filename1, self.filename2, "ciphertext.txt", 'CFB')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under CFB Mode!')
            elif mode == 'OFB模式':
                encrypt_AES_file(self.filename1, self.filename2, "ciphertext.txt", 'OFB')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under OFB Mode!')
            elif mode == 'CTR模式':
                encrypt_AES_file(self.filename1, self.filename2, "ciphertext.txt", 'CTR')
                secret.reset()
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under CTR Mode!')
            else:
                messagebox.showinfo('Message', '您还未选择加密模式！')

    # 解密函数（含异常处理）        
    def decrypt(self):
        # 密文文本路径为空，报错
        if self.filename3 == "":
            messagebox.showinfo('Message', '您还未选择密文文本！')
        # 解密密钥文本路径为空，报错
        elif self.filename4 == "":
            messagebox.showinfo('Message', '您还未选择密钥文本！')
        else:
            mode = self.combobox2.get()
            if mode == 'ECB模式':
                decrypt_AES_file(self.filename3, self.filename4, "result.txt", 'ECB')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under ECB Mode!')
            elif mode == 'CBC模式':
                decrypt_AES_file(self.filename3, self.filename4, "result.txt", 'CBC')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under CBC Mode!')
            elif mode == 'CFB模式':
                decrypt_AES_file(self.filename3, self.filename4, "result.txt", 'CFB')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under CFB Mode!')
            elif mode == 'OFB模式':
                decrypt_AES_file(self.filename3, self.filename4, "result.txt", 'OFB')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under OFB Mode!')
            elif mode == 'CTR模式':
                decrypt_AES_file(self.filename3, self.filename4, "result.txt", 'CTR')
                messagebox.showinfo('Message', 'Success encrypt plaintext file: ' + self.filename1 + ' using password file ' + self.filename2 + ' under CTR Mode!')
            else:
                messagebox.showinfo('Message', '您还未选择加密模式！')

# 实例化窗体类
gui = GraphicInterface()
# 主消息循环:
gui.mainloop()