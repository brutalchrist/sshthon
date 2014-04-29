#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from gi.repository import Gtk, Vte, GLib

class Terminal(Gtk.Window):
	def __init__(self, *args, **kwds):
		Gtk.Window.__init__(self, title=args[0]["nombre"]+" ["+args[0]["usuario"]+"@"+args[0]["ip"]+"]")
		self.set_size_request(600, 400)

		comando = "ssh " + args[0]["usuario"] + "@" + args[0]["ip"] + "\n"

		terminal = Vte.Terminal()
		terminal.connect('realize', self.onRealize, comando)
		terminal.connect('destroy', self.onDestroy)
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

	def onDestroy(self, terminal):
		self.destroy()
