#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import glob
import json

from os.path import expanduser
from time import gmtime, strftime
from gi.repository import Gtk, Vte, GLib, Gdk, Gio, GdkPixbuf

SSHTHON_DIR = expanduser("~")+"/.sshthon"

class sshthonWindow(Gtk.ApplicationWindow):
	def __init__(self, app):
		Gtk.Window.__init__(self, title="sshThon", application=app)
		self.set_border_width(10)

		self.crearDirectorioSshthon()
		vbox = self.crearVentana()
		self.cargarVentana(vbox)

	def crearVentana(self):
		hbox = Gtk.Box(spacing=6)
		self.add(hbox)
		
		vbox_principal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		hbox.pack_start(vbox_principal, True, True, 0)

		return vbox_principal

	def cargarVentana(self, vbox_principal):
		listaJSON = []
		directorioRaiz = os.getcwd()

		os.chdir(SSHTHON_DIR)
		for jsons in glob.glob("*.json"):
			listaJSON.append(jsons)

		listaJSON.sort()

		for file in listaJSON:
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

		os.chdir(directorioRaiz)

	def crearDirectorioSshthon(self):
		if not os.path.exists(SSHTHON_DIR):
			log("Creando directorio "+SSHTHON_DIR)
			os.makedirs(SSHTHON_DIR)		

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
		

class SshThonAplicacion(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self)
	
	def do_activate(self):
		win = sshthonWindow(self)
		win.show_all()

	def do_startup(self):
		Gtk.Application.do_startup(self)

		# Acciones menu
		nuevoAction = Gio.SimpleAction.new("new", None)
		nuevoAction.connect("activate", self.doClickNuevo)
		self.add_action(nuevoAction)

		salirAction = Gio.SimpleAction.new("quit", None)
		salirAction.connect("activate", self.doClickSalir)
		self.add_action(salirAction)

		acercaDeAction = Gio.SimpleAction.new("acercaDe", None)
		acercaDeAction.connect("activate", self.doClickAcercaDe)
		self.add_action(acercaDeAction)

		# Cargar menu
		builder = Gtk.Builder()
		try:
			builder.add_from_file("menu.ui")
		except:
			print "Archivo menu.ui no encontrado"
			sys.exit()

		self.set_menubar(builder.get_object("menubar"))

	def doClickNuevo(self, action, parameter):
		print("Nuevo")

	def doClickSalir(self, action, parameter):
		sys.exit()

	def doClickAcercaDe(self, action, parameter):
		print("Acerca de")
		aboutdialog = Gtk.AboutDialog()

		authors = ["Sebastián González Villena "]

		aboutdialog.set_program_name("sshThon")
		aboutdialog.set_copyright("Copyright \xc2\xa9 2012 GNOME Documentation Team")
		aboutdialog.set_authors(authors)
		aboutdialog.set_website("http://developer.gnome.org")
		aboutdialog.set_website_label("GNOME Developer Website")
		aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_size("imagenes/sshthon.png", 100, 100))

		aboutdialog.connect("response", self.on_close)

		aboutdialog.show()

	def on_close(self, action, parameter):
		action.destroy()
		

if __name__ == '__main__':
	app = SshThonAplicacion()
	exit_status = app.run(sys.argv)
	sys.exit(exit_status)
