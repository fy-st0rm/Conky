import tkinter as tk
import tkinter.font as tkFont
import json
import os
from datetime import datetime
import platform
import psutil
import shutil
import getpass


class Conky:
	def __init__(self):
		# Reading the config file
		self.config_file = {}
		self.__read_config()
	
		# Week days
		self.days = {
			0: "Mon",
			1: "Tue",
			2: "Wed",
			3: "Thur",
			4: "Fri",
			5: "Sat",
			6: "Sun"
		}

		# Parsing the config file
		self.pos = self.config_file["pos"]
		self.size = self.config_file["size"]
		self.alpha = self.config_file["alpha"]
		self.bg = self.config_file["bg"]
		self.fg = self.config_file["fg"]
		self.font = self.config_file["font"]
		self.font_size = self.config_file["font_size"]

		# Creating pannel
		self.__create_pannel()

		self.tk_font = tkFont.Font(family = self.font, size = self.font_size)
		
		self.__ui()

	def __read_config(self):
		with open(os.path.join("config.json"), "r") as json_file:
			self.config_file = json.load(json_file)			
	
	def __create_pannel(self):
		self.root = tk.Tk()
		self.root.resizable(False, False)

		if platform.system() == "Linux":
			self.root.attributes("-type", "desktop")
		elif platform.system() == "Windows":
			self.root.overrideredirect(True)

		# Assigning size and position
		self.root.geometry(f"{self.size[0]}x{self.size[1]}+{self.pos[0]}+{self.pos[1]}")

		# Assigning alpha value
		if platform.system() == "Linux":
			self.root.wait_visibility(self.root)
			self.root.wm_attributes("-alpha", self.alpha)
		elif platform.system() == "Windows":
			self.root.attributes("-transparentcolor", self.bg)

		self.canvas = tk.Canvas(self.root, width = self.size[0], height = self.size[1], bg = self.bg)
		self.canvas.pack()

	# Ui developments
	def __ui(self):
		self.__display_time()
		self.__display_date()
		self.__display_sys_info()

	def __update_ui(self):
		# Updating time	
		now = datetime.now()

		current_time = now.strftime("%H:%M:%S")
		hr = current_time.split(":")[0]
		mi = current_time.split(":")[1]
		se = current_time.split(":")[2]

		meridiem = "AM"
		if int(hr) > 12: 
			hr = int(hr) - 12
			meridiem = "PM"
		
		current_time = str(hr) + ":" + mi + ":" + se

		self.time_label.configure(text = current_time + " " + meridiem)

		# Updating day and date
		today = datetime.today()
		date = today.strftime("%m:%d:%Y")
		day = self.days[today.weekday()]

		text = day + " " + date
		self.date_label.configure(text = text)

		self.__update_sys()

		self.root.after(int(1000/30), self.__update_ui)

	def __display_time(self):
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")

		hr = current_time.split(":")[0]
		mi = current_time.split(":")[1]
		se = current_time.split(":")[2]

		meridiem = "AM"
		if int(hr) > 12: 
			hr = int(hr) - 12
			meridiem = "PM"
		
		current_time = str(hr) + ":" + mi + ":" + se

		# Rendering time in the canvas
		time_frame = tk.Frame(self.canvas)
		time_frame.place(relx = 0.64, rely = 0.03, relwidth = 0.35, relheight = 0.06)

		self.time_label = tk.Label(time_frame, text = current_time + " " + meridiem, bg = self.bg, fg = self.fg)
		self.time_label.pack(expand = True, fill = "both")
		self.time_label.config(font = (self.font, self.font_size + 7))

	def __display_date(self):
		today = datetime.today()
		date = today.strftime("%m:%d:%Y")
		day = self.days[today.weekday()]
		
		# Rendering day and date in the canvas
		date_frame = tk.Frame(self.canvas)
		date_frame.place(relx = 0.69, rely = 0.09, relwidth = 0.3, relheight = 0.05)
	
		text = day + " " + date
		self.date_label = tk.Label(date_frame, text = text, bg = self.bg, fg = self.fg)
		self.date_label.pack(expand = True, fill = "both")
		self.date_label.config(font = (self.font, self.font_size))

	# System UIs
	def __insert(self, tag, value, pos = "down"):
		if pos == "up":
			space = ((len("username") - len(tag)) + 33) - len(value)
		elif pos == "down":
			space = ((len("usage") - len(tag)) +29) - len(value)
		self.sys_info_frame.insert("end", "|" + " " * 7 + "+---" + tag + ":" + " " * space + value + "\n")
	
	def __update_sys(self):	
		# Updating sys infos
		self.sys_info_frame.configure(state = "normal")
		self.sys_info_frame.delete(1.0, "end")
		
		#Top divider
		self.sys_info_frame.insert("end", "+" + "-" * 53 + "+\n")
	
		# System info	
		os_name = platform.system()
		version = platform.release()
		username = getpass.getuser()

		self.sys_info_frame.insert("end", "+" + "-"  * 7  + "System:\n")
		self.sys_info_frame.insert("end", "|" + " " * 7  + "|\n")
		self.__insert("username", username, "up")
		self.__insert("os", os_name, "up")
		self.__insert("ver", version, "up")
		
		# applying the uptime only if its a linux device
		if os_name == "Linux":
			uptime = os.popen("uptime -p").read()[:-1]
			self.__insert("uptime", uptime, "up")

		# System status
		self.sys_info_frame.insert("end", "|\n")
		self.sys_info_frame.insert("end", "+" + "-" * 7 + "Status:\n")

		# CPU:
		self.sys_info_frame.insert("end", "|" + " " * 7 + "|\n")
		self.sys_info_frame.insert("end", "|" + " " * 7 + "+------CPU:\n")
	
		# calulation cpu usage
		load1, load5, load15 = psutil.getloadavg() 
		cpu_usage = (load15/os.cpu_count()) * 100
		
		self.sys_info_frame.insert("end", "|" + " " * 7)
		self.__insert("Usage", str(round(cpu_usage, 2)) + "%")

		# RAM:	
		self.sys_info_frame.insert("end", "|" + " " * 7 + "|\n")
		self.sys_info_frame.insert("end", "|" + " " * 7 + "+------RAM:\n")
	
		# calulation cpu usage
		ram_usage = psutil.virtual_memory()[2]
		total_ram = round(((psutil.virtual_memory().total / 1024) / 1024) / 1024, 2)

		self.sys_info_frame.insert("end", "|" + " " * 7)
		self.__insert("Total", str(total_ram) + " GB")
		self.sys_info_frame.insert("end", "|" + " " * 7)
		self.__insert("Usage", str(ram_usage) + "%")

		# Disk
		total, used, free = shutil.disk_usage("/")

		self.sys_info_frame.insert("end", "|" + " " * 7 + "|\n")
		self.sys_info_frame.insert("end", "|" + " " * 7 + "+------Disk:\n")
		
		self.sys_info_frame.insert("end", "|" + " " * 7)
		self.__insert("Total", str(total // (2**30)) + " GB")

		self.sys_info_frame.insert("end", "|" + " " * 7)
		self.__insert("Used", str(used // (2**30)) + " GB")
		
		self.sys_info_frame.insert("end", "|" + " " * 7)
		self.__insert("Free", str(free // (2**30)) + " GB")

		# Battery 
		battery = psutil.sensors_battery()
		percent = int(battery.percent)
		plugged = battery.power_plugged

		self.sys_info_frame.insert("end", "|" + " " * 7 + "|\n")
		self.sys_info_frame.insert("end", "|" + " " * 7 + "+------Battery:\n")

		self.sys_info_frame.insert("end", "|" + " " * 7)
		self.__insert("Percent", str(percent) + "%")
		self.sys_info_frame.insert("end", "|" + " " * 7)
		self.__insert("Plugged", str(plugged))

		# Ending header
		self.sys_info_frame.insert("end", "|" + " " * 7 + "|\n")
		self.sys_info_frame.insert("end", "+" + "-" * 53 + "+")

		self.sys_info_frame.configure(state = "disabled")
		
	def __display_sys_info(self):
		info_frame = tk.Frame(self.canvas, bg = self.bg)
		info_frame.place(relx = 0.01, rely = 0.15, relwidth = 0.98, relheight = 0.85)

		# Rendering system info
		self.sys_info_frame = tk.Text(info_frame, bg = self.bg, fg = self.fg, font = (self.font, self.font_size))
		self.sys_info_frame.pack(expand = True, fill = "both")
		self.sys_info_frame.configure(state = "disabled")

	# Funtion to run the conky
	def run(self):
		self.root.after(int(1000/30), self.__update_ui)
		self.root.mainloop()


if __name__ == "__main__":
	conky = Conky()
	conky.run()

