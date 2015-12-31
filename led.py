#!/usr/bin/python3

# A little project that turns an RGB LED into a weather forecast indicator.
# Read the accompanying README for details.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from gi.repository import GLib
import gi
gi.require_version('GWeather', '3.0')
from gi.repository import GWeather

import gpiozero as gp

class LED(gp.RGBLED):
    def __init__(self, red, green, blue):
        gp.RGBLED.__init__(self, red, green, blue)
        self.off()
        self._blink_source = 0

    def blink(self, color):
        self.stop_blink()
        self._blink_color = color
        self._blink_source = GLib.timeout_add(500, self._blink_cb)

    def stop_blink(self):
        self.value = (0, 0, 0)
        if self._blink_source == 0:
            return

        GLib.source_remove(self._blink_source)
        self._blink_source = 0

    def show_weather(self, info):
        self.stop_blink()

        print('%s\n' % (info.get_weather_summary()))
        [ret, sky] = info.get_value_sky()
        if not ret:
            return

        if sky <= GWeather.Sky.SCATTERED:
            self.value = (1, 1, 0)
        else:
            self.value = (0, 0, 1)

    def _blink_cb(self):
        if self.value == (0, 0, 0):
            self.value = self._blink_color
        else:
            self.value = (0, 0, 0)

        return True
