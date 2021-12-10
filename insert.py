import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from tkinter.constants import *
import cv2
import math
import json

config=open('config.json','r')
json_config=json.load(config)

class Block():
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        # 图像定位
        self.picx = 0
        self.picy = 0
        # 插入图片
        self.img = cv2.imread(json_config['ImgName']['insertPic'], cv2.IMREAD_UNCHANGED)
        self.row = self.img.shape[0]
        self.col = self.img.shape[1]
        # 对图片更改格式以应用于tkinter
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGRA2RGBA)
        tkimg = ImageTk.PhotoImage(Image.fromarray(self.img))
        self.item = self.canvas.create_image(0, 0, anchor='nw', image=tkimg)
        self.lbPic = tk.Label(text='test', width=400, height=600)
        self.lbPic['image'] = tkimg
        self.lbPic.image = tkimg
        self.set_item_mapping()
        # 在画布上图片的属性
        self.scale = 1  # 缩放
        self.angle = 0  # 角度
        self.M = None  # 由角度得到的仿射变换矩阵

        # 原始图片的角点
        self.initialpic = np.float32([[0, 0], [self.col - 1, 0], [0, self.row - 1], [self.col - 1, self.row - 1]])
        # 透视变换后的角点
        self.newpic = np.float32([[0, 0], [self.col - 1, 0], [0, self.row - 1], [self.col - 1, self.row - 1]])
        self.H = None  # 透视变换矩阵
        self.delta = json_config['delta']  # 每次修改透视变换角点的幅度

        self.outsize = math.ceil(math.sqrt((self.row) ** 2 + (self.col) ** 2) / 2)  # 图片外接圆
        self.intersize = 0  # 图像保真圆

    def changepic(self):  # 该函数对插入图像羽化处理
        img = self.img
        center = [self.row / 2, self.col / 2]
        for i in range(self.row):
            for j in range(self.col):
                den = math.sqrt((i - center[0]) ** 2 + (j - center[1]) ** 2)
                if (den > self.outsize):
                    img[i][j][3] = 0
                elif (den <= self.outsize and den > self.intersize):
                    rate = 1 - (den - self.intersize) / (self.outsize - self.intersize)
                    img[i][j][3] = int(255 * rate)
                else:
                    img[i][j][3] = 255
        self.img = img

    def freshpic(self, im):#该函数在你更改图片属性后，对画布上的图片进行更新
        self.canvas.delete(self.item)
        tkim = ImageTk.PhotoImage(Image.fromarray(im))
        self.item = self.canvas.create_image(self.picx, self.picy, anchor='center', image=tkim)
        self.set_item_mapping()

        self.lbPic['image'] = tkim
        self.lbPic.image = tkim

    def changeIntersize(self, event):#改变内圆的大小，由拖动条触发
        self.intersize = int(event)
        self.changepic()

    def changeOutsize(self, event):#改变外圆的大小，由拖动条触发
        self.outsize = int(event)
        self.changepic()

    def move_to(self, x: float, y: float):#移动图片
        self.picx = x
        self.picy = y
        self.canvas.move_to(self.item, x, y)

    def set_item_mapping(self):
        self.canvas.itemMap[self.item] = self

    def rsz(self, size):#更改图片大小
        self.scale = self.scale * size
        M = cv2.getRotationMatrix2D((self.col / 2, self.row / 2), self.angle, 1)
        self.M = M

        im = cv2.warpAffine(self.img, M, (self.col, self.row))

        try:
            im = cv2.warpPerspective(im, self.H, (self.col, self.row))
            im = cv2.resize(im, (0, 0), fx=self.scale, fy=self.scale)
        except:
            im = cv2.resize(im, (0, 0), fx=self.scale, fy=self.scale)

        self.freshpic(im)

    def rotate(self, angle):#旋转图片
        col = self.img.shape[0]
        row = self.img.shape[1]
        self.angle = angle
        M = cv2.getRotationMatrix2D((col / 2, row / 2), self.angle, 1)

        self.M = M
        im = cv2.warpAffine(self.img, M, (row, col))

        try:
            im = cv2.warpPerspective(im, self.H, (self.col, self.row))
            im = cv2.resize(im, (0, 0), fx=self.scale, fy=self.scale)
        except:
            im = cv2.resize(im, (0, 0), fx=self.scale, fy=self.scale)
        self.freshpic(im)

    def buttonLeftShrink(self):#由按钮触发，触发使得图片左边缩小，相当于人眼右移的透视变换
        d = self.delta
        self.newpic[0][1] = self.newpic[0][1] + d
        self.newpic[2][1] = self.newpic[2][1] - d
        self.H = cv2.getPerspectiveTransform(self.initialpic, self.newpic)

        self.perspective_pic()

    def buttonRightShrink(self):#由按钮触发，触发使得图片右边缩小，相当于人眼左移的透视变换
        d = self.delta
        self.newpic[1][1] = self.newpic[1][1] + d
        self.newpic[3][1] = self.newpic[3][1] - d
        self.H = cv2.getPerspectiveTransform(self.initialpic, self.newpic)

        self.perspective_pic()

    def buttonUpShrink(self):#由按钮触发，触发使得图片上边缩小，相当于人眼下移的透视变换
        d = self.delta
        self.newpic[0][0] = self.newpic[0][0] + d
        self.newpic[1][0] = self.newpic[1][0] - d
        self.H = cv2.getPerspectiveTransform(self.initialpic, self.newpic)

        self.perspective_pic()

    def buttonDownShrink(self):#由按钮触发，触发使得图片下边缩小，相当于人眼上移的透视变换
        d = self.delta
        self.newpic[2][0] = self.newpic[2][0] + d
        self.newpic[3][0] = self.newpic[3][0] - d
        self.H = cv2.getPerspectiveTransform(self.initialpic, self.newpic)

        self.perspective_pic()

    def perspective_pic(self):#对图片透视变换
        try:
            im = cv2.warpAffine(self.img, self.M, (self.col, self.row))
            im = cv2.warpPerspective(im, self.H, (self.col, self.row))
            im = cv2.resize(im, (0, 0), fx=self.scale, fy=self.scale)
        except:
            im = cv2.warpPerspective(self.img, self.H, (self.col, self.row))
            im = cv2.resize(im, (0, 0), fx=self.scale, fy=self.scale)

        self.freshpic(im)


class MyCanvas(tk.Canvas):#画布重定义对象
    def __init__(self, parent):
        super().__init__(parent)
        self.itemToMove = None
        self.relativePos = ()
        self.sc = tk.Scale(parent, from_=-90, to=90, orient=tk.HORIZONTAL, command=self.rotate_pic, showvalue=True)
        self.sc.set(0)  # 设置初始值
        self.sc.pack(expand=0, fill=tk.X)

        self.itemMap = {}  # 东西的映射。当拖动等事件发生时，修改这个字典中的对象。
        self.bind('<ButtonPress-1>', self.on_mouse_down)
        self.bind('<B1-Motion>', self.on_mouse_drag)
        self.bind("<MouseWheel>", self.processWheel)



    def on_mouse_down(self, event):
        self.relativePos = ()
        a = self.find_withtag(tk.CURRENT)
        if len(a) >= 1:
            coor = self.coords(a[0])
            x, y = event.x - coor[0], event.y - coor[1]
            self.relativePos = (x, y)

            self.itemToMove = a[0]
        else:
            self.itemToMove = None

    def move_to(self, item_id, x, y):
        pos = self.coords(item_id)
        self.move(item_id, x - pos[0], y - pos[1])

    def on_mouse_drag(self, event):
        if not self.itemToMove:  # 如果没有要移动的对象，就直接return,防止出现奇奇怪怪的错误。
            return

        a = self.find_withtag(tk.CURRENT)
        if len(a) >= 1:
            self.itemMap[a[0]].move_to(event.x - self.relativePos[0], event.y - self.relativePos[1])

    def rotate_pic(self, event):
        angle = int(event)


        src = self.itemMap[2]
        src.rotate(angle)

    def processWheel(self, event):
        a = self.find_withtag(tk.CURRENT)

        if len(a) >= 1:
            src = self.itemMap[a[0]]
            if event.delta > 0:
                src.rsz(json_config["scaleSize"])
            # 滚轮往上滚动，放大
            else:
                src.rsz(1/json_config["scaleSize"])
        # 滚轮往下滚动，缩小

if __name__=='__main__':
    master = tk.Tk()
    bg_image = cv2.imread(json_config['ImgName']['backgroundPic'])#修改背景图片
    bg_image = cv2.cvtColor(bg_image, cv2.COLOR_BGR2RGB)
    bgw = bg_image.shape[1]
    bgh = bg_image.shape[0]
    windowW = master.winfo_screenwidth()
    windowH = master.winfo_screenheight()
    if json_config["adjustWindow"]:
        windowscale = min(0.7*windowW / bgw,0.7*windowH/bgh)
        bg_image = cv2.resize(bg_image, (0, 0), fx=windowscale, fy=windowscale)

    bg = ImageTk.PhotoImage(Image.fromarray(bg_image))

    master.geometry(str(int(0.9*windowW)) + 'x' + str(int(0.9*windowH)))
    w = MyCanvas(master)
    w.create_image(0, 0, anchor='nw', image=bg)
    w.pack(fill=tk.BOTH, expand=1)
    b = Block(w)

    #########控制透视变换的按钮们######
    ButtonFrame_l = tk.Frame(master, relief=RAISED, borderwidth=2)
    ButtonFrame_l.pack(side=LEFT, fill=BOTH, ipadx=13, ipady=13, expand=0)

    ls = tk.Button(ButtonFrame_l, text='左缩', command=b.buttonLeftShrink)
    ls.pack(side=LEFT)
    rs = tk.Button(ButtonFrame_l, text='右缩', command=b.buttonRightShrink)
    rs.pack(side=RIGHT)
    ds = tk.Button(ButtonFrame_l, text='下缩', command=b.buttonDownShrink)
    ds.pack(side=BOTTOM)
    us = tk.Button(ButtonFrame_l, text='上缩', command=b.buttonUpShrink)
    us.pack(side=TOP)
    ##########控制透明区域的滑条############
    outsizebar = tk.Scale(master, from_=0, to=180, orient=tk.HORIZONTAL, command=b.changeOutsize, showvalue=True)
    outsizebar.set(180)  # 设置初始值
    outsizebar.pack(expand=0, fill=tk.X)
    intersizebar = tk.Scale(master, from_=0, to=180, orient=tk.HORIZONTAL, command=b.changeIntersize, showvalue=True)
    intersizebar.set(0)  # 设置初始值
    intersizebar.pack(expand=0, fill=tk.X)

    tk.mainloop()


def pic2png(picpath):
    pass