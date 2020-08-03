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

#pacmd set-sink-port 0 analog-output-lineout
#pactl list sinks

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


    def GetSources(self):
        out = subprocess.Popen(['pacmd','list-sinks'],\
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        lines = stdout.decode("utf-8").split("\n")
        
        sources = {}

        for line in lines:
            if "index" in line:
                
                active, number = line.replace(" ","").split('index:')
                sources[number] = {}
                
                if active == "*":
                    sources[number]["active"] = True
                else:
                    sources[number]["active"] = False
            else:

                if "device.description" in line:
                    description = line.split("device.description = ")[-1]
                    description = description.replace('"',"")
                    sources[number]["device_description"] = description

                if "(priority" in line: #filter active ports
                     
                    port = line.split(": ")[0]
                    port = port.replace("\t","")
                    port_description = line.split(": ")[1].split(" (")[0]

                    if not("ports" in sources[number].keys()):
                        sources[number]["ports"] = {}

                    if not(port in sources[number].keys()):
                        sources[number]["ports"][port] = {}
                        sources[number]["ports"][port]["description"] = port_description

                if "active port:" in line: #filter active ports description
                    
                    active_port = line.split(": ")[-1]
                    active_port = active_port.replace("<","")
                    active_port = active_port.replace(">","")

                    sources[number]["active_port"] = active_port 

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

    def SetActiveSource(self, index):
        out = subprocess.Popen(['pacmd','set-default-sink',index],\
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()



class Indicator():

    def __init__(self):
        self.ind = ind = appindicator.Indicator.new("sound-source-indicator","" ,\
                appindicator.IndicatorCategory.APPLICATION_STATUS)
        
        folder = "/usr/share/icons/HighContrast/22x22/devices/"
        head_phone = "headphones.png" 
        line_out = "audio-card.png"
        hdmi_dp = "video-display.png"

        #ind.set_title("teste")
        ind.set_status (appindicator.IndicatorStatus.ACTIVE)
        #ind.set_attention_icon("indicator-messages-new")
        ind.set_icon_full(folder + line_out,"Sound source indicator icon")

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

            menu_items.connect("activate", self.OnClickItem, id_)
            menu_items.show()

        ind.set_menu(menu)

        Gtk.main()


    def OnClickItem(self, widget,_id):
        index = self.sources.GetSourcesIndex()[_id]
        self.sources.SetActiveSource(index)


if __name__ == "__main__":

    #ind = Indicator()

    s = SoundSources()
    sources = s.GetSources()

    for dev in sources.keys():
        if sources[dev]["active"] == True:
            for port in sources[dev]["ports"].keys():
                print(port)

    print("\n\n")
    print(sources)
