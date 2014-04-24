#!/usr/bin/env python
import os
from os.path import expanduser
import glob
from time import gmtime, strftime

import json
from gi.repository import Gtk, Vte, GLib, Gdk

SSHTHON_DIR = expanduser("~")+"/.sshthon"

class sshthonWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="sshThon")
		self.set_border_width(10)

		if not os.path.exists(SSHTHON_DIR):
			log("Creando directorio "+SSHTHON_DIR)
			os.makedirs(SSHTHON_DIR)

		hbox = Gtk.Box(spacing=6)
		self.add(hbox)
		
		vbox_principal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		hbox.pack_start(vbox_principal, True, True, 0)

		os.chdir(SSHTHON_DIR)
		for file in glob.glob("*.json"):
			hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
			vbox_principal.add(hbox)
			separador = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
			vbox_principal.add(separador)
			vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
			hbox.pack_start(vbox, True, True, 0)

			json_data=open(SSHTHON_DIR+"/"+file)
			data = json.load(json_data)

			labelNombre = Gtk.Label(data["nombre"], xalign=0)
			labelIP = Gtk.Label(data["ip"], xalign=0)
			labelDescripcion = Gtk.Label(data["descripcion"], xalign=0)
			vbox.pack_start(labelNombre, True, True, 0)
			vbox.pack_start(labelIP, True, True, 0)
			vbox.pack_start(labelDescripcion, True, True, 0)
			botonConectar = Gtk.Button(label="Conectar")
			botonConectar.connect("clicked", self.onClickConectar, data)
			hbox.pack_start(botonConectar, False, True, 0)

			json_data.close()	

	def onClickConectar(self, widget, data):		
		self.log("Conectando a " + data["ip"] + 
				" con el usuario " + data["usuario"] + 
				" ["+data["nombre"]+"]")

		t = Terminal(data)
		t.show_all()

	def log(self, mensaje):
		print("\033[1m\033[36m" + 
				strftime("%d-%m-%Y %H:%M:%S", gmtime()) + 
				":\033[0m \033[1m" + mensaje + "\033[0m")

class Terminal(Gtk.Window):
	def __init__(self, *args, **kwds):
		Gtk.Window.__init__(self, title=args[0]["nombre"]+" ["+args[0]["usuario"]+"@"+args[0]["ip"]+"]")
		self.set_size_request(600, 400)

		comando = "ssh " + args[0]["usuario"] + "@" + args[0]["ip"] + "\n"

		terminal = Vte.Terminal()
		terminal.connect('realize', self.onRealize, comando)
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.add(terminal)

		self.add(scrolledwindow)

		terminal.fork_command_full(
			Vte.PtyFlags.DEFAULT,
			os.environ['HOME'],
			["/bin/sh"],
			[],
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None,
			None,
			)	

	def onRealize(self, terminal, comando):
		terminal.feed_child(comando, len(comando))
		

if __name__ == '__main__':
	win = sshthonWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
