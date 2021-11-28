# myapp.py
from random import random

from bokeh.layouts import column
from bokeh.models import Button, Dropdown
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
import os
import c_fua_polygons

# Polygon dict
poly_dict = {}

# Walk the results directory
for root, dirs, files in os.walk("C:/USRA/FUA_Processing/outputs"):
    # For each file name
    for name in files:
        poly_dict[name.split('_')[0]] = name


# create a plot and style its properties
p = figure(toolbar_location=None)
p.border_fill_color = 'black'
p.background_fill_color = 'black'
p.outline_line_color = None
p.grid.grid_line_color = None

# add a text renderer to the plot (no data yet)
r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="26px",
           text_baseline="middle", text_align="center")

# Add a line rendered to the plot (no data yet)
ts_data = p.line(x=[], y=[], legend_label="NTL", line_width=2)

i = 0

ds = r.data_source
ts_ds = ts_data.data_source

# create a callback that adds a number in a random location
def callback():
    global i

    # BEST PRACTICE --- update .data in one step with a new dict
    new_data = dict()
    new_data['x'] = ds.data['x'] + [random()*70 + 15]
    new_data['y'] = ds.data['y'] + [random()*70 + 15]
    new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
    new_data['text'] = ds.data['text'] + [str(i)]
    ds.data = new_data


    i = i + 1

def dropdown_cb(event):

    curr_poly = c_fua_polygons.FUAPolygon()
    curr_poly.load_from_json(f"C:/USRA/FUA_Processing/outputs/{poly_dict[str(event.item)]}")
    days, ntls = curr_poly.get_time_series()

    new_data = dict()
    new_data['x'] = days
    new_data['y'] = ntls
    new_data["legend_label"] = str(event.item)
    ts_ds.data = new_data

# add a button widget and configure with the call back
button = Button(label="Press Me")
button.on_click(callback)

# add a select menu widget
dropdown = Dropdown(label="FUA Polygon", button_type="warning", menu=list(poly_dict.keys()))
dropdown.on_click(dropdown_cb)
# put the button and plot in a layout and add to the document
curdoc().add_root(column(button, p, dropdown))