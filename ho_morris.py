from fltk import *
import os
import subprocess as sp
import signal
import platform

class mp3player(Fl_Window):
	def __init__(self, w, h, label = None):

		self.last = 0 #pos of last song
		self.dfiles = {} #dict for songs
		self.playing = False #sets playing state

		#window
		Fl_Window.__init__(self,w,h,label)
		self.begin()

		#Menubar
		
		menu = Fl_Menu_Bar(0,0,w,25)
		menu.add("Add/Directory",100, self.addcb)
		menu.add("Clear/All",FL_ALT|97, self.clrcb)
		menu.add("Go/First",102,self.firstcb)
		menu.add("Go/Playing",112, self.cplaycb)
		menu.add("Go/Last",108,self.lastcb)
		
		#output
		self.out = Fl_Output(0,25,w,25)
		self.out.color(FL_YELLOW)
		
		#Browser
		self.brow = Fl_Hold_Browser(0,50,w,270)

		#Buttons
		Pack = Fl_Pack(0,320,w,80)
		Pack.begin()

		back_but = Fl_Button(0,self.h()-80,80,80,'@|<')
		back_but.tooltip("Previous (ALT <-)")
		back_but.shortcut(FL_ALT|FL_Left)
		back_but.callback(self.backcb)

		play_but = Fl_Button(80,self.h()-80,80,80,'@>')
		play_but.tooltip("Play (Enter)")
		play_but.shortcut(FL_Enter)
		play_but.callback(self.playcb)

		next_but = Fl_Button(160,self.h()-80,80,80,'@>|')
		next_but.tooltip("Next (ALT ->)")
		next_but.shortcut(FL_ALT|FL_Right)
		next_but.callback(self.nextcb)

		stop_but = Fl_Button(240,self.h()-80,80,80,'@square')
		stop_but.tooltip("Stop (ALT S)")
		stop_but.shortcut(FL_ALT|115)
		stop_but.callback(self.stopcb)

		del_but = Fl_Button(320,self.h()-80,80,80,'@undo')
		del_but.tooltip("Remove (Delete)")
		del_but.shortcut(FL_Delete)
		del_but.callback(self.delcb)

		Pack.end()
		Pack.type(FL_HORIZONTAL)

		self.callback(self.closewin)
		self.end()
		self.resizable(self.brow)

	#MENUBAR METHODS
	#add files to playlist
	def addcb(self,wid):
		di = fl_dir_chooser("Open directory","")
		li = os.listdir(di)
		for name in li:
			if name[-4:] in ('.mp3'):
				self.brow.add(name[:-4])
				self.dfiles[name[:-4]] = os.path.normpath(os.path.join(di,name))
				self.last +=1
		self.brow.select(1)

	#clear files from playlist
	def clrcb(self,wid):
		self.brow.clear()
		self.delcb(self.brow)
		self.last == 0
		if self.playing == True:
			self.proc.send_signal(signal.SIGTERM)
			self.playing = False
			self.out.value('')


	#go to first
	def firstcb(self,wid):
		self.brow.select(1)

	#to to current
	def cplaycb(self,wid):					
		self.brow.select(self.playingV)

		
	#go to last
	def lastcb(self,Fl_Browser_):
		self.brow.select(self.last)

	#BUTTS METHODS
		
	#plays previous song	
	def backcb(self,wid):
		try:
			self.proc.send_signal(signal.SIGTERM)
			self.playing = False
		except:
			pass

		pos = self.brow.value()
		if pos == 1:
			self.brow.select(self.last)
		else:
			self.brow.select(self.brow.value()-1)
		self.playcb(self.brow)

	#play song
	def playcb(self,wid):
		try:	
			if self.playing == False:
				if platform.system() == "Windows":
					self.proc = sp.Popen(['C:\Program Files (x86)\VideoLAN\VLC\VLC.exe','--intf','dummy',self.dfiles.get(self.brow.text(self.brow.value()))])
					self.playing = True
					self.out.value(self.brow.text(self.brow.value()))
					self.playingV = self.brow.value()

				elif platform.system() == "Linux":
					self.proc = sp.Popen(['vlc','--intf','dummy',self.dfiles.get(self.brow.text(self.brow.value()))])
					self.playing = True

			elif self.playing == True:
				try:
					self.proc.send_signal(signal.SIGTERM)
					self.playing = False
				except:
					pass
				self.playcb(self.brow)
		except:
			pass

	#plays next song
	def nextcb(self,wid):
		try:
			self.proc.send_signal(signal.SIGTERM)
			self.playing = False
		except:
			pass

		pos = self.brow.value()
		if pos == self.last:
			self.brow.select(1)
		else:
			self.brow.select(self.brow.value()+1)
		self.playcb(self.brow)

	#stop song
	def stopcb(self,wid):
		if self.playing == True:
			self.proc.send_signal(signal.SIGTERM)
			self.playing = False
			self.out.value('')

	#del files
	def delcb(self,wid):
		pos = self.brow.value()
		self.brow.remove(pos)
		self.brow.select(pos)

		if pos == self.playingV:
			if self.playing == True:
				self.proc.send_signal(signal.SIGTERM)
				self.playing = False
				self.out.value('')
				self.last -= 1
		else:
			self.last -= 1

	#SYNTAX METHODS
	#close win
	def closewin(self,wid):
		try:
			if self.playing == True:
				self.proc.send_signal(signal.SIGTERM)
				self.playing = False
				wid.hide()
			else:
				wid.hide()
		except:
			wid.hide()
		
app = mp3player(400,400,"MP3 Player")
app.show()
Fl.run()
