import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading
import qrcode
from PIL import Image, ImageTk
from threading import Timer
import random
from pylibdmtx.pylibdmtx import encode
from pylibdmtx.pylibdmtx import decode


def foo(delay):
    print(f'foo() called after {delay}s delay')

#Работа с QR кодом
def qrcode_gen(i):
   #img = qrcode.make('01046200326515282151N(rM93M6nW')
   #type(img)
   #img.save(f'c:/222/img.png')
   qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=5,
                border=4,
            )
   num = random.randint(0, 125)
   code='01046200326515282151N(rM93M6nW'+str(num)
   qr.add_data(code)
   qr.make(fit=True)
   #qr_image = qr.make_image(fill_color="black", back_color="white")
   encoded = encode(code.encode('utf8'))
   qr_image = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
   barcode_lb.config(text = code)
   return qr_image

window = Tk()
window.title('Генерация штрих-кодов')
window.geometry('400x400')

i = 0 


#encoded = encode('hello world'.encode('utf8'))
#img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
#img.save('c:/222/dmtx.png')
#print(decode(Image.open('c:/222/dmtx.png')))


def code_start():
   global i
   i=0
   code_clear()
   code_show()

def code_show():
   #delay = 4
   global i
   i = i + 1
   if (i%2!=0):
    img = qrcode_gen(i)
    qr_photo = ImageTk.PhotoImage(img)
    barcode_img_lb.config(image = qr_photo)
    barcode_img_lb.image = qr_photo
    numx = random.randint(0, 50)
    numy = random.randint(0, 50)
    barcode_img_lb.place(x=50+numx, y=50+numy)
    window["bg"] = "black"
   else:
     window["bg"] = "red"
     code_clear()    
   if (i<40):
      window.after(500,code_show)


def code_clear():
   barcode_img_lb.config(text="")
  # barcode_img_lb.image = ""

barcode_img_lb = Label(
   #frame,
   text=""
)
#barcode_img_lb.grid(row=0, column=0)
barcode_img_lb.place(x=50, y=50)

barcode_lb = Label(
   #frame,
   text="ШК: "
)
#barcode_lb.grid(row=1, column=0)
barcode_lb.place(x=10, y=10)


cal_btn_tb = Button(
   #frame,
   text='Показать ШК',
   command=code_start
)
#cal_btn_tb.grid(row=3, column=0)
cal_btn_tb.place(x=40, y=30)


cal_btn_tb = Button(
   #frame,
   text='Очистить',
   command=code_clear
)
#cal_btn_tb.grid(row=3, column=2)
cal_btn_tb.place(x=180, y=30)



window.mainloop()
