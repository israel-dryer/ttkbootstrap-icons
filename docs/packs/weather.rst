Weather Icons
=============

Erik Flowers' forecast set, and the more systematic of the two weather packs. Every condition has a day and a night drawing, the moon phases are all there, and there are wind-direction and Beaufort-scale glyphs that nothing else in the catalogue carries.

What makes it worth choosing over :doc:`meteocons` is that it maps directly onto weather APIs. The set ships aliases named after the condition codes that OpenWeatherMap, Weather Underground, and Forecast.io return, so you can turn an API response into an icon without writing the lookup table yourself.

.. pack-preview:: weather

Using it
--------

.. pack-install:: weather

.. code-block:: python

   from tkinter_icons import WeatherIcon

   sunny = WeatherIcon("day-sunny", size=32)
   clear_night = WeatherIcon("night-clear", size=32)
   storm = WeatherIcon("thunderstorm", size=32)

Straight from an API response
-----------------------------

The code-mapped names make this a one-liner. OpenWeatherMap returns a numeric condition code and a day/night flag:

.. code-block:: python

   def forecast_icon(code, is_day, size=32):
       part = "day" if is_day else "night"
       return WeatherIcon(f"owm-{part}-{code}", size=size)

   forecast_icon(500, is_day=True)     # light rain, daytime

``owm-<code>`` without the day/night segment works too, and the same shape applies to ``wu-`` for Weather Underground and ``forecast-io-`` for Forecast.io:

.. code-block:: python

   WeatherIcon("owm-802")
   WeatherIcon("wu-partlycloudy")
   WeatherIcon("forecast-io-clear-day")

Names
-----

Upstream prefixes everything ``wi-``, and both spellings resolve:

.. code-block:: python

   WeatherIcon("wi-day-sunny")
   WeatherIcon("day-sunny")   # the same glyph

Pack details
------------

.. pack-facts:: weather
