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

from time import sleep
from threading import Thread

from weather_color import WeatherColor

class LED(gp.RGBLED):
    def __init__(self, red, green, blue):
        gp.RGBLED.__init__(self, red, green, blue)
        self.off()
        self._blink_color = None
        self._blink_times = 0
        self._blink_callback = None
        self._blink_thread = None

    def close(self):
        self.stop_blink()
        gp.RGBLED.close(self)

    def blink(self, color, times=0, callback=None):
        self.stop_blink()
        self._blink_color = color
        self._blink_times = times
        self._blink_callback = callback
        self._blink_thread = Thread(target=self._blink_func)
        self._blink_thread.start()

    def stop_blink(self):
        if self._blink_color == None:
            return

        self._blink_color = None
        self._blink_thread.join()
        self.value = (0, 0, 0)
        self._blink_callback = None

    def show_weather(self, info):
        self.stop_blink()

        if info == None:
            # No weather => unlit LED
            self.value = (0, 0, 0)
            return

        print('%s\n' % (info.get_weather_summary()))
        [ret, sky] = info.get_value_sky()
        if not ret:
            return

        if sky <= GWeather.Sky.SCATTERED:
            self.value = WeatherColor.SUNNY
        else:
            self.value = WeatherColor.HY_RAIN

    def _blink_func(self):
        blinked = 0
        while self._blink_color != None and (self._blink_times == 0 or blinked <= self._blink_times):
            if self.value == (0, 0, 0):
                self.value = self._blink_color
            else:
                self.value = (0, 0, 0)
                blinked = blinked + 1
            sleep(0.5)
        if self._blink_callback != None:
            GLib.idle_add(self._blink_callback)
