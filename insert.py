import tkinter as tk
from PIL import Image, ImageTk

import cv2

class Block():
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.picx=0
        self.picy=0
        self.img=cv2.imread('m1.png',cv2.IMREAD_UNCHANGED)
        self.img=cv2.cvtColor(self.img,cv2.COLOR_BGRA2RGBA)
        #self.img=self.img[:,:,::-1,:]#bgr->rgb

        tkimg=ImageTk.PhotoImage(Image.fromarray(self.img))
        self.item=self.canvas.create_image(0, 0,anchor='nw',image=tkimg)
        self.lbPic = tk.Label(text='test', width=400, height=600)
        self.lbPic['image'] = tkimg
        self.lbPic.image = tkimg
        #self.lbPic.pack(fill=tk.BOTH, expand=tk.YES)

        self.set_item_mapping()
        self.scale=1


    def move_to(self, x: float, y: float):
        self.picx=x
        self.picy=y
        self.canvas.move_to(self.item, x, y)

    def set_item_mapping(self):

        self.canvas.itemMap[self.item] = self

    def rsz(self,size:float,x,y):
        self.canvas.delete(self.item)
        self.scale = self.scale * size
        im = cv2.resize(self.img, (0, 0), fx=self.scale, fy=self.scale)
        tkim = ImageTk.PhotoImage(Image.fromarray(im))
        self.item = self.canvas.create_image(x, y, anchor='center', image=tkim)
        self.set_item_mapping()


        self.lbPic['image'] = tkim
        self.lbPic.image = tkim
    def rotate(self,angle):

        self.canvas.delete(self.item)
        col=self.img.shape[0]
        row=self.img.shape[1]
        M = cv2.getRotationMatrix2D((col/2,row/2),angle,1)
        im=cv2.warpAffine(self.img,M,(row,col))
        tkim = ImageTk.PhotoImage(Image.fromarray(im))
        self.item = self.canvas.create_image(self.picx, self.picy, anchor='center', image=tkim)
        self.set_item_mapping()

        self.lbPic['image'] = tkim
        self.lbPic.image = tkim

class MyCanvas(tk.Canvas):
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
            print('ok')
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


    def rotate_pic(self,event):
        angle=int(event)
        print(angle)

        src = self.itemMap[2]
        src.rotate(angle)



    def processWheel(self,event):
        a = self.find_withtag(tk.CURRENT)

        if len(a) >= 1:
            src=self.itemMap[a[0]]
            if event.delta > 0:
                src.rsz(1.1,event.x,event.y)
            # 滚轮往上滚动，放大
            else:
                 src.rsz(0.9,event.x,event.y)
        # 滚轮往下滚动，缩小

canvas_width = 1900
canvas_height = 1500

master = tk.Tk()

image=cv2.imread('m1.png',cv2.IMREAD_UNCHANGED)
im=ImageTk.PhotoImage(Image.fromarray(image))
bg_image=cv2.imread('bg1.jpg')
bg=ImageTk.PhotoImage(Image.fromarray(bg_image))
bgw=bg_image.shape[0]
bgh=bg_image.shape[1]
master.geometry(str(bgw)+'x'+str(bgh))
w = MyCanvas(master)
w.create_image(0,0,anchor='nw',image=bg)
w.pack(fill=tk.BOTH, expand=1)

print(w.find_all())
b = Block(w)

tk.mainloop()


def pic2png(picpath):
    pass