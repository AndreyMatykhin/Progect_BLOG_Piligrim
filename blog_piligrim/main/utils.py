import os
from secrets import token_hex
from PIL import Image

from flask import current_app


def save_picture(form_picture, dir_path):
    random_hex = token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, dir_path, picture_fn)
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

from branca.element import MacroElement

from jinja2 import Template

class LatLngPopup(MacroElement):
    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent("Установить метку здесь" +
                                    "<br>Latitude: " + e.latlng.lat.toFixed(4) +
                                    "<br>Longitude: " + e.latlng.lng.toFixed(4))
                        .openOn({{this._parent.get_name()}});
                    parent.document.getElementById("latitude").value = e.latlng.lng; 
                    parent.document.getElementById("longitude").value = e.latlng.lat; 
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """)  # noqa

    def __init__(self):
        super(LatLngPopup, self).__init__()
        self._name = 'LatLngPopup'