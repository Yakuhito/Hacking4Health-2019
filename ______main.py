#-------

APP_WIDTH = 1280
APP_HEIGHT = 720

print_coords = False

#-------

from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

import serial
import sys
import subprocess
import threading
import time
import random
import os


import numpy as np


moves = []
times = [] # for plot data
root = "" # Root 
C = "" # Main Canvas
C2 = "" # Plots & stuff
start_button = "" # Start button
start_time = 0 # Used to measure the time that has passed
round_started = False
force_exit = False
max_time = 100.0
time_label = ""
you_label = ""
add_move = True

c_plot1 = ""
c_plot2 = ""


pi = "" # The garbage collector will never find it here...


PLOT_MAX = 100
to_plot = [int(i - i) for i in range(PLOT_MAX)]
to_plot1 = [int(i - i) for i in range(PLOT_MAX)]

photoimage = ""


from PIL import Image

file_in = 'crosshair.png'
pil_image = Image.open(file_in)

image100x100 = pil_image.resize((100 // 2, 100 // 2), Image.ANTIALIAS)

file_out = 'crosshair.png'
image100x100.save(file_out)



def motion(event):
	x, y = event.x, event.y
	print('Coords: {}, {}'.format(x, y))


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

last_rep = ""

def updateMoves():
	global moves
	global last_rep
	nv = moves[-1]
	posx = [370, 210, 210, 370]
	posy = [180, 180, 220, 220]
	print("[*] Moves: {}".format(len(moves)))
	dx = 0
	dy = 0
	n = 0
	for i in range(len(nv)):	
		if nv[i] == 0:
			#print(i)
			dx += posx[i]
			dy += posy[i]
			n += 1
	if n == 0:
		if last_rep != "":
			C.delete(last_rep)
			last_rep = ""
		return False
	if last_rep != "":
			C.delete(last_rep)
			last_rep = ""
	dx = dx / n
	dy = dy / n
	# Modify coords a lil' bit
	dx += int((int(random.random() * 100) - 50) / 5 * 2)
	dy += int((int(random.random() * 100) - 50) / 5 * 2)
	last_rep = C.create_image(dx, dy, image=photoimage)

last_time = time.time()

def processData(v):
	global add_move
	global moves
	global times
	global last_rep
	global photoimage
	global C
	global last_time
	nv = []
	posx = [370, 210, 210, 370]
	posy = [180, 180, 220, 220]
	#print(v)
	nv.append(v[1])
	nv.append(v[2])
	nv.append(v[0])
	nv.append(v[3])
	print("[*] Data: {}".format(nv))
	if (len(moves) == 0 or add_move) and nv != [1, 1, 1, 1]:
			moves.append(nv)
			times.append(time.time())
			add_move = False
			updateMoves()
	if nv == [1, 1, 1, 1]:
			add_move = True
			if last_rep != "":
				C.delete(last_rep)
				last_rep = ""
	#C.create_image(370, 160, image=photoimage)

	while len(times) > 1 and time.time() - times[0] > 5.0:
		times = times[1:]
	
	x = time.time()

	if add_move:
		frecv2 = 0
	else:
		frecv2 = 1


	if time.time() - last_time > 1.5:
		frecv1 = 1
		last_time = time.time()
	else:
		frecv1 = 0


	global to_plot
	global to_plot1
	global PLOT_MAX
	to_plot = to_plot[len(to_plot) - PLOT_MAX + 1:]
	to_plot1 = to_plot1[len(to_plot1) - PLOT_MAX + 1:]
	#to_plot.append(frecv)
	#print(len(to_plot))
	to_plot1.append(frecv1)
	to_plot.append(frecv2)


def arduinoThread():
	global round_started
	global force_esxit
	ser = serial.Serial(getInterf())
	while not force_exit:
		try:
			v = []
			data = ser.readline().decode().replace("\r\n", "")
			v = [int(i) for i in data.split(" ")]
			if round_started:
				processData(v)
		except Exception as e:
			print("arduinoThread")
			print(e)
			pass
	print("[*] ArduinoThread - quit!")


def roundThread():
	global force_exit
	global start_time
	global time_label
	global moves
	
	while not force_exit and time.time() - start_time < max_time:
		tp = time.time() - start_time
		if int(tp) % 60 > 9: 
			time_label.config(text = "{}:{}/{}".format(int(tp) // 60, int(tp) % 60, len(moves)))
		else:
			time_label.config(text = "{}:0{}/{}".format(int(tp) // 60, int(tp) % 60, len(moves)))

	force_exit = True
	print("[*] RoundThread - quit!")


dataimg2 = ""
img2 = ""
dataimg1 = ""
img1 = ""


def plotData(arr):
	plt.cla()
	plt.clf()
	plt.close()
	plt.plot([i for i in range(len(arr))], arr, c='black')
	plt.xticks([])
	plt.yticks([])
	plt.savefig("data.png")


def refreshPlots():
	global c_plot1
	global c_plot2
	global dataimg2
	global to_plot
	global img2
	global dataimg1
	global to_plot1
	global img1

	#print("REFRESH!")

	
	os.system("rm data.png")
	plotData(to_plot)
	file_in = 'data.png'
	pil_image = Image.open(file_in)

	image100x100 = pil_image.resize((580, 200), Image.ANTIALIAS)

	file_out = 'data.png'
	image100x100.save(file_out)

	c_plot2.delete("all")

	dataimg2 = ImageTk.PhotoImage(file="data.png")
	a = c_plot2.create_image(290, 100, image=dataimg2)

	os.system("rm data.png")
	plotData(to_plot1)
	file_in = 'data.png'
	pil_image = Image.open(file_in)

	image100x100 = pil_image.resize((580, 200), Image.ANTIALIAS)

	file_out = 'data.png'
	image100x100.save(file_out)

	c_plot1.delete("all")

	dataimg1 = ImageTk.PhotoImage(file="data.png")
	a = c_plot1.create_image(290, 100, image=dataimg1)


def drawThread():
	while True:
		refreshPlots()
		time.sleep(0.5)


def startRound():
	global round_started
	global time_label
	global force_exit
	global start_button
	global start_time
	global you_label
	global root
	global pi
	global C
	global C2
	global c_plot1
	global c_plot2

	print("[*] Starting round...")

	start_button.destroy()

	start_time = time.time()

	print("[*] Start time: {}".format(start_time))

	round_started = True

	time_label = Label(root, text="0:00/0")
	time_label.config(font=("Courier", 44))
	time_label.pack()

	C = Canvas(root, bg="white", height=600, width=600)
	C.place(x=25, y=95)

	pi = PhotoImage(file="torso.png")
	torso_img = C.create_image(300, 300, image=pi)

	C2 = Canvas(root, bg="white", height=600, width=600)
	C2.place(x=655, y=95)

	target_label = Label(C2, text = "Normal", font=("Courier", 40))
	target_label.place(x=10, y=20)

	you_label = Label(C2, text = "Pacient", font=("Courier", 40))
	you_label.place(x=10, y=320)

	c_plot1 = Canvas(C2, bg="white", height=200, width=580)
	c_plot1.place(x=10, y=90)

	c_plot2 = Canvas(C2, bg="white", height=200, width=580)
	c_plot2.place(x=10, y=390)

	t = threading.Thread(target=roundThread)
	t.start()

	t2 = threading.Thread(target=drawThread)
	t2.start()


def main():
	global start_button
	global root
	global C
	global photoimage

	print("[*] Starting...")

	root  = Tk()
	root.wm_title("QUBE. Demo")

	root.geometry(("{}x{}+0+0").format(APP_WIDTH, APP_HEIGHT))


	if print_coords:
		root.bind('<Motion>', motion)

	photoimage = ImageTk.PhotoImage(file="crosshair.png")

	t = threading.Thread(target=arduinoThread)
	t.start()

	start_button = Button(root, text="Start", command=startRound, font=("Courier", 60))
	start_button.place(x=490, y=300)

	root.mainloop()


if __name__ == "__main__":
		main()