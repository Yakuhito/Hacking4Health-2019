# ---------
print_coords = False
# ---------

from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

import serial
import sys
import subprocess
import threading

print("[*] Starting...")

top = Tk()
#top.resizable(width=False, height=False)
top.geometry("1280x720+0+0")

C = Canvas(top, bg="black", height=720, width=1278)
#filename = PhotoImage(file = "background.png")
#background_label = Label(top, image=filename)
#background_label.place(x=0, y=0)
#C.tag_lower(background_label)
pi = PhotoImage(file="background.png")
C.create_image(639, 360, image=pi)
C.pack()

# Never, ever do this!
#C.master.overrideredirect(True)

#C.create_image(360, 639, image=img)

#C.pack()


commnet = """def create_circle(x, y, r, canvasName): #center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvasName.create_oval(x0, y0, x1, y1, fill="#00ff00", outline="")"""

photoimage = ImageTk.PhotoImage(file="crosshair.png")

#scale_w = 50 / photoimage.width()
#scale_h = 50 / photoimage.height()

#photoimage.zoom(scale_w, scale_h)

from PIL import Image

file_in = 'crosshair.png'
pil_image = Image.open(file_in)

image100x100 = pil_image.resize((100 // 2, 100 // 2), Image.ANTIALIAS)

file_out = 'crosshair.png'
image100x100.save(file_out)

def create_circle(x, y, r, canvasName): #center coordinates, radius
	#x0 = x - r
	#y0 = y - r
	#x1 = x + r
	#y1 = y + r
	global photoimage
	img = canvasName.create_image(x, y, image=photoimage)
	return img
	#img.pack()
	#return img

#lc = "NEIN"

def motion(event):
	global C
	global lc
	x, y = event.x, event.y
	print('Coords: {}, {}'.format(x, y))
	#crc = create_circle(x, y, 20, C)
	#if lc != "NEIN":
	#	C.delete(lc)
	#lc = crc
	#C.pack()


def getInterf():
	base_str = "/dev/ttyUSB{}"
	for i in range(10):
		try:
			print("[*] Scanning interface {}".format(i))
			ser = serial.Serial(base_str.format(i))
			print("[*] Found device on /dev/ttyUSB{}".format(i))
			return base_str.format(i)
		except:
			continue
	print("[!] Something went very, very, very wrong. Please check your device's connection and try again")
	sys.exit(1)


if print_coords:
	top.bind('<Motion>', motion)

c1, c2, c3, c4 = "NULL", "NULL", "NULL", "NULL"

drawn_c = "NULL"

def processData(v):
	global C
	global c1, c2, c3, c4, drawn_c
	print("[*] Data: {}".format(v))
	nv = []
	nv.append(v[0])
	nv.append(v[3])
	nv.append(v[2])
	nv.append(v[1])
	vx = [690, 610, 610, 690]
	vy = [200, 200, 230, 230]
	dx = 0
	dy = 0
	n = 0
	for i in range(len(nv)):
		if nv[i] == 0:
			n += 1
			dx += vx[i]
			dy += vy[i]
	if n == 0:
		if drawn_c != "NULL":
			C.delete(drawn_c)
			drawn_c = "NULL"
	else:
		dx = dx / n
		dy = dy / n
		if drawn_c != "NULL":
			C.delete(drawn_c)
			drawn_c = "NULL"
		drawn_c = create_circle(dx, dy, 20, C)
	comment = """print(nv)
	if nv[0] == 1:
		try:
			C.delete(c1)
		except Exception as e:
			print(e)
			pass
		c1 = "NULL"
	else:
		if c1 == "NULL":
			c1 = create_circle(670, 200, 20, C)
	if nv[1] == 1:
		try:
			C.delete(c2)
		except Exception as e:
			print(e)
			pass
		c2 = "NULL"
	else:
		if c2 == "NULL":
			c2 = create_circle(620, 200, 20, C)
	if nv[2] == 1:
		try:
			C.delete(c3)
		except Exception as e:
			print(e)
			pass
		c3 = "NULL"
	else:
		if c3 == "NULL":
			c3 = create_circle(620, 230, 20, C)
	if nv[3] == 1:
		try:
			C.delete(c4)
		except Exception as e:
			print(e)
			pass
		c4 = "NULL"
	else:
		if c4 == "NULL":
			c4 = create_circle(670, 230, 20, C)"""
	C.pack()


def arduinoThread():
	ser = serial.Serial(getInterf())
	while True:
		try:
			v = []
			data = ser.readline().decode().replace("\r\n", "")
			v = [int(i) for i in data.split(" ")]
			processData(v)
		except Exception as e:
			print(e)
			pass


t = threading.Thread(target=arduinoThread)
t.start()

top.mainloop()
