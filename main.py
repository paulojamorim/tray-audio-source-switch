#!/usr/bin/env python

"""
Copyright (C) 2020 - Paulo Henrique Junqueira Amorim

Tray-audio-source-switch - Allows to switch the audio source 
(headphone, HDMI etc.) on the Indicator Applet of the GNOME Classic.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  
02110-1301, USA.
"""


#sudo apt-get install libgtk-3-dev libgirepository1.0-dev
#pip install PyGObject
#sudo apt-get install gir1.2-appindicator3-0.1

import re
import subprocess
import gi
gi.require_version('AppIndicator3', '0.1') 
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib
from gi.repository import AppIndicator3 as appindicator

class SoundSources():

    def __init__(self):
        pass

    def GetActiveSourceIndex(self):
        out = subprocess.Popen(['pacmd','list-sinks'],\
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        lines = stdout.decode("utf-8").split("\n")

        index = None
        for l in lines:
            if '*' in l:
                index = re.findall(r'\d+',l)[-1]
                break

        return index

    def GetSourcesDescription(self):
        out = subprocess.Popen(['pacmd','list-sinks'],\
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        lines = stdout.decode("utf-8").split("\n")
        
        sources = []

        for l in lines:
            if 'device.description' in l:

                description = l.split("device.description = ")[-1]
                description = description.replace('"','')
                sources.append(description)

        return sources

    def GetSourcesIndex(self):
        out = subprocess.Popen(['pactl','list','sinks','short'],\
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        lines = stdout.decode("utf-8").split("\n")
        
        sources = []

        for l in lines:
            index = re.findall(r'\d+',l)
            if index != []:
                sources.append(index[0])

        return sources



class Indicator():

    def __init__(self):
        self.ind = ind = appindicator.Indicator.new("sound-source-indicator","" ,\
                appindicator.IndicatorCategory.APPLICATION_STATUS)
        f = '/usr/share/icons/ubuntu-mono-dark/status/22/indicator-keyboard-Ur-3.svg'
        #ind.set_title("teste")
        ind.set_status (appindicator.IndicatorStatus.ACTIVE)
        #ind.set_attention_icon("indicator-messages-new")
        ind.set_icon_full(f,"Sound source indicator icon")

        self.sources = sources = SoundSources()
        sources_description = sources.GetSourcesDescription()
        
        menu = Gtk.Menu()
        self.menus = menus = []
        
        for id_, sd in enumerate(sources_description):
            if menus != []:
                menu_items = Gtk.RadioMenuItem(label=str(sd), group=self.menus[0])
            else:
                menu_items = Gtk.RadioMenuItem(label=sd)

            menus.append(menu_items)
            menu.append(menu_items)

            menu_items.connect("activate", self.menuitem_response)
            menu_items.show()

        ind.set_menu(menu)

        Gtk.main()


    def menuitem_response(self, w):
        print(dir(w))
        #w.set_active(False)
        #print(dir(w))
        for i in range(len(self.menus)):
            if w is self.menus[i]:
                print(w)
               #w.set_active(False)
               #break
            if self.menus[i] != w:
                self.menus[i].set_active(False)

        #print(self.menus[1])
        #    #print("")
        #    if menu != w:
        #        menu.set_active(False)
        #    #else:
        #    #    menu.set_active(True)

if __name__ == "__main__":

    ind = Indicator()
