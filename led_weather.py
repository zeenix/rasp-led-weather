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

gi.require_version('Geoclue', '2.0')
from gi.repository import Geoclue

from pins import Pins
from led import LED

class LEDWeather:
    def __init__(self):
        self._show_timeout = 0
        self._first_update = True
        self._led = LED(Pins.RED, Pins.GREEN, Pins.BLUE)
        self._led.blink((1, 0, 0))
        self._simple = Geoclue.Simple.new('geoclue-where-am-i', # Let's cheat
                                          Geoclue.AccuracyLevel.EXACT,
                                          None,
                                          self._on_simple_ready)

    def close(self):
        self._unshedule_weather_show()
        self._led.close()

    def _on_simple_ready(self, simple, data):
        location = simple.get_location()

        self._on_location_updated(location)

    def _on_location_updated(self, location):
        latitude = location.get_property('latitude')
        longitude = location.get_property('longitude')

        world = GWeather.Location.get_world()
        city = world.find_nearest_city(latitude, longitude)
        self.info = GWeather.Info.new(city, GWeather.ForecastType.LIST)
        self.info.set_enabled_providers(GWeather.Provider.METAR | GWeather.Provider.YR_NO)

        self.info.connect('updated', self._on_weather_updated, None)
        self._update_timeout = GLib.timeout_add_seconds(3600, self._on_weather_update_timeout)

    def _on_weather_update_timeout(self):
        self._unshedule_weather_show()
        self._led.blink((1, 0, 0))
        self.info.update()

        return True

    def _on_weather_updated(self, info, data):
        self._unshedule_weather_show()

        self._index = 0

        if self._first_update:
            self._show_weather()
            self._first_update = False

        self._show_timeout = GLib.timeout_add_seconds(5, self._show_weather)

    def _show_weather(self):
        forecasts = self.info.get_forecast_list()
        if self._index >= len(forecasts) or self._index >= 72:
            self._index = 0
            self._led.show_weather(None)

            return True;

        print("Weather in %d hours" % self._index)
        self._led.show_weather(forecasts[self._index])
        self._index = self._index + 12

        return True

    def _unshedule_weather_show(self):
        if self._show_timeout == 0:
            return

        GLib.source_remove(self._show_timeout)
        self._show_timeout = 0
