import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput, Select
from bokeh.plotting import figure
import os
import c_fua_polygons
import datetime

# Polygon dict
poly_dict = {}

# Walk the results directory
for root, dirs, files in os.walk("C:/USRA/FUA_Processing/outputs"):
    # For each file name
    for name in files:
        poly_dict[name.split('_')[0]] = name

# Set up data
N = 200
x = []
y = []
source = ColumnDataSource(data=dict(x=x, y=y))
ra_source = ColumnDataSource(data=dict(x=x, y=y))

# Set up plot
plot = figure(height=400, width=800, title="FUA Polygon Timeseries",
              tools="crosshair,pan,reset,save,wheel_zoom", x_axis_type='datetime', y_range=[0, 35],
              x_range=[datetime.datetime(year=2012, month=1, day=19), datetime.datetime(year=2014, month=1, day=1)])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)
plot.line('x', 'y', source=ra_source, line_width=3, line_color='Red')

# Set up widgets
ra_slider= Slider(title="Rolling Average", value=0, start=0, end=30, step=1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)

# add a select menu widget
dropdown = Select(options=list(poly_dict.keys()))


# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value


def update_ts_data(attr, old, new):

    curr_poly = c_fua_polygons.FUAPolygon()
    curr_poly.load_from_json(f"C:/USRA/FUA_Processing/outputs/{poly_dict[str(new)]}")
    days, ntls = curr_poly.get_time_series()
    plot.x_range.bounds = (days[0], days[-1])
    #p.y_range.factors = (int(np.min(ntls)), int(np.max(ntls)))
    # Generate the new curve
    x = days
    y = ntls
    # update the source data
    source.data = dict(x=x, y=y)
    # update the ra data
    update_ra_data('value', old, ra_slider.value)

def update_ra_data(attr, old, new):

    ra_poly = c_fua_polygons.FUAPolygon()
    ra_poly.load_from_json(f"C:/USRA/FUA_Processing/outputs/{poly_dict[dropdown.value]}")
    days, ntls = ra_poly.get_rolling_average(int(new))
    #plot.x_range.bounds = (days[0], days[-1])
    # p.y_range.factors = (int(np.min(ntls)), int(np.max(ntls)))
    # Generate the new curve
    x = days
    y = ntls

    ra_source.data = dict(x=x, y=y)

# for w in [offset, amplitude, phase, freq]:
#     w.on_change('value', update_data)
ra_slider.on_change('value', update_ra_data)

dropdown.on_change('value', update_ts_data)

# Set up layouts and add to document
inputs = column(ra_slider, dropdown)

curdoc().add_root(column(inputs, plot, width=800))
curdoc().title = "EfSI Interactive"