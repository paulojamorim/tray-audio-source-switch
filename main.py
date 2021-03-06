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



    def SetActiveSource(self, port, device_name):

        out = subprocess.Popen(['pacmd','set-default-sink',port],\
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()

        out = subprocess.Popen(['pacmd','set-sink-port', port, device_name],\
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()



class Indicator():

    def __init__(self):
        self.ind = ind = appindicator.Indicator.new("sound-source-indicator","" ,\
                appindicator.IndicatorCategory.HARDWARE) 
        ind.set_status (appindicator.IndicatorStatus.ACTIVE)

        # Take audio sources
        source =  self.source = SoundSources()
        sources = source.GetSources()
        
        devices_items = self.devices_items = []

        for dev in sources.keys():
            for port in sources[dev]["ports"].keys():
                devices_items.append((dev, sources[dev]["active"], port,\
                        sources[dev]["ports"][port]["description"], 
                        sources[dev]["active_port"]))
                
                print((dev, sources[dev]["active"], port,\
                        sources[dev]["ports"][port]["description"], 
                        sources[dev]["active_port"]))

        # Create menu etc
        menu = Gtk.Menu()
        self.menus = menus = []
        
        for id_, sd in enumerate(devices_items):
            if menus != []:
                menu_items = Gtk.RadioMenuItem(label=str(devices_items[id_][3]),\
                        group=self.menus[0])
            else:
                menu_items = Gtk.RadioMenuItem(label=devices_items[id_][3])

            menus.append(menu_items)            
            menu.append(menu_items)

        
            if (devices_items[id_][1] == True) and\
                    (devices_items[id_][2] == devices_items[id_][4]):
                        widget = menus[id_]
                        widget.set_active(True)
                        self.SetIcon(widget, self.devices_items[id_][3])


            menu_items.connect("activate", self.OnClickItem, id_)
            menu_items.show()

        ind.set_menu(menu)

        Gtk.main()

    def SetIcon(self, widget, description):

        folder = "/usr/share/icons/HighContrast/22x22/devices/"
        head_phone = "headphones.png" 
        line_out = "audio-card.png"
        hdmi_dp = "video-display.png"

        if "HDMI" in description:
            icon = hdmi_dp
        elif "Headphone" in description:
            icon = head_phone
        else:
            icon = line_out

        self.ind.set_icon_full(folder + icon,"Sound source indicator icon")

    def OnClickItem(self, widget,_id):
        if widget.get_active():
            device = self.devices_items[_id]
            self.source.SetActiveSource(device[0],device[2])
            self.SetIcon(widget, device[3]) 
        return True

if __name__ == "__main__":

    ind = Indicator()
