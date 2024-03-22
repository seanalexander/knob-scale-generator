#! /usr/bin/python
'''
Copyright (C) 2017 Artem Synytsyn a.synytsyn@gmail.com

#TODO: Code cleaning and refactoring

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import inkex
import sys
from lxml import etree
from math import *

class Knob_Scale(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        # General settings
        self.arg_parser.add_argument("--x",
                        type=float,
                        dest="x", default=0.0,
                        help="Center X")
        self.arg_parser.add_argument("--y",
                        type=float,
                        dest="y", default=0.0,
                        help="Center Y")
        self.arg_parser.add_argument("--radius",
                        type=float,
                        dest="radius", default=100.0,
                        help="Knob radius")
        self.arg_parser.add_argument("--linewidth",
                        type=float,
                        dest="linewidth", default=1,
                        help="")
        self.arg_parser.add_argument("--angle",
                        type=float,
                        dest="angle", default=260.0,
                        help="Angle of the knob scale in degrees")
        self.arg_parser.add_argument("--draw_arc",
                        type=inkex.Boolean,
                        dest="draw_arc", default='True',
                        help="")
        self.arg_parser.add_argument("--draw_centering_circle",
                        type=inkex.Boolean,
                        dest="draw_centering_circle", default='False',
                        help="")
        self.arg_parser.add_argument("-u", "--units",
                        type=str,
                        dest="units", default="px",
                        help="units to measure size of knob")
        # Tick settings
        self.arg_parser.add_argument("--n_ticks",
                        type=int,
                        dest="n_ticks", default=5,
                        help="")
        self.arg_parser.add_argument("--ticksize",
                        type=float,
                        dest="ticksize", default=10,
                        help="")
        self.arg_parser.add_argument("--n_subticks",
                        type=int,
                        dest="n_subticks", default=10,
                        help="")
        self.arg_parser.add_argument("--subticksize",
                        type=float,
                        dest="subticksize", default=5,
                        help="")
        self.arg_parser.add_argument("--style",
                        type=str,
                        dest="style", default='marks_outwards',
                        help="Style of marks")

        # Label settings
        self.arg_parser.add_argument("--labels_enabled",
                        type=inkex.Boolean,
                        dest="labels_enabled", default='False',
                        help="")
        self.arg_parser.add_argument("--rounding_level",
                        type=int,
                        dest="rounding_level", default=0,
                        help="")
        self.arg_parser.add_argument("--text_size",
                        type=float,
                        dest="text_size", default=1,
                        help="")
        self.arg_parser.add_argument("--text_offset",
                        type=float,
                        dest="text_offset", default=20,
                        help="")
        self.arg_parser.add_argument("--start_value",
                        type=float,
                        dest="start_value", default=0,
                        help="")
        self.arg_parser.add_argument("--stop_value",
                        type=float,
                        dest="stop_value", default=10,
                        help="")
        # Dummy
        self.arg_parser.add_argument("--tab")

    def draw_text(self, textvalue, radius, angular_position, text_size, parent):
        # Create text element
        text = etree.Element(inkex.addNS('text','svg'))
        text.text = textvalue

        # Set text position to center of document.
        text.set('x', str(self.x_offset + radius*cos(angular_position)))
        text.set('y', str(self.y_offset + radius*sin(angular_position) + text_size/2))

        # Center text horizontally with CSS style.
        style = {
                'text-align' : 'center',
                 'text-anchor': 'middle',
                 'alignment-baseline' : 'central',
                 'font-size' : str(text_size),
                 'vertical-align' : 'middle'
                 }

        text.set('style', str(inkex.Style(style)))
        parent.append(text)
    def draw_knob_arc(self, radius, parent, angle, transform='' ):

        start_point_angle = (angle - pi)/2.0
        end_point_angle = pi - start_point_angle

        style = {   'stroke'        : '#000000',
                    'stroke-width'  : str(self.options.linewidth),
                    'fill'          : 'none'            }
        ell_attribs = {'style': str(inkex.Style(style)),
            inkex.addNS('cx','sodipodi')        :str(self.x_offset),
            inkex.addNS('cy','sodipodi')        :str(self.y_offset),
            inkex.addNS('rx','sodipodi')        :str(radius),
            inkex.addNS('ry','sodipodi')        :str(radius),
            inkex.addNS('start','sodipodi')     :str(end_point_angle),
            inkex.addNS('end','sodipodi')       :str(start_point_angle),
            inkex.addNS('open','sodipodi')      :'true',    #all ellipse sectors we will draw are open
            inkex.addNS('type','sodipodi')      :'arc',
            'transform'                         :transform

                }
        ell = etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )

    def draw_centering_circle(self, radius, parent):

        style = {   'stroke'        : '#000000',
                    'stroke-width'  : '1',
                    'fill'          : 'none'            }
        ell_attribs = {'style':str(inkex.Style(style)),
            inkex.addNS('cx','sodipodi')        :str(self.x_offset),
            inkex.addNS('cy','sodipodi')        :str(self.y_offset),
            inkex.addNS('rx','sodipodi')        :str(radius),
            inkex.addNS('ry','sodipodi')        :str(radius),
            inkex.addNS('type','sodipodi')      :'arc'
            }
        ell = etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )

    def draw_circle_mark(self, x_offset, y_offset, radius, mark_angle, mark_length, parent):

        cx = x_offset + radius*cos(mark_angle)
        cy = y_offset + radius*sin(mark_angle)
        r = mark_length / 2.0

        style = {
                'stroke': '#000000',
                'stroke-width':'0',
                'fill': '#000000'
                }

        circ_attribs = {
                'style':str(inkex.Style(style)),
                'cx':str(cx),
                'cy':str(cy),
                'r':str(r)
                }
        circle = etree.SubElement(parent, inkex.addNS('circle','svg'), circ_attribs )

    def draw_knob_line_mark(self, x_offset, y_offset, radius, mark_angle, mark_length, parent):
        x1 = x_offset + radius*cos(mark_angle)
        y1 = y_offset + radius*sin(mark_angle)
        x2 = x_offset + (radius + mark_length)*cos(mark_angle)
        y2 = y_offset + (radius + mark_length)*sin(mark_angle)

        line_style   = { 'stroke': '#000000',
                         'stroke-width': str(self.options.linewidth),
                         'fill': 'none'
                       }

        line_attribs = {'style' : str(inkex.Style(line_style)),
                        inkex.addNS('label','inkscape') : "none",
                        'd' : 'M '+str(x1) +',' +
                        str(y1) +' L '+str(x2)
                        +','+str(y2) }

        line = etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )

    def draw_tick(self, radius, mark_angle, mark_size, parent):
        if (self.options.style == 'marks_inwards') or (self.options.style == 'marks_outwards'):
            self.draw_knob_line_mark(self.x_offset, self.y_offset, radius, mark_angle, mark_size, parent)
        elif self.options.style == 'marks_circles':
            self.draw_circle_mark(self.x_offset, self.y_offset, radius, mark_angle, mark_size, parent)

    def get_tick_angles(self):
        angle = radians(self.options.angle)
        n_ticks = self.options.n_ticks
        ticks_delta = angle / (n_ticks - 1)
        start_angle = 1.5*pi - 0.5*angle
        return [start_angle + ticks_delta * i for i in range(n_ticks)]

    def get_tick_labels(self):
        start_num = self.options.start_value
        end_num = self.options.stop_value
        n_ticks = self.options.n_ticks
        rounding_level = self.options.rounding_level
        if rounding_level <= 0:
            rounding_level = None

        labels = []
        label_delta = (end_num - start_num) / (n_ticks - 1)
        for tick in range(n_ticks):
            num = start_num + tick * label_delta
            tick_text = str(round(num, rounding_level))
            labels.append(tick_text)
        return labels

    def get_subtick_angles(self):
        angle = radians(self.options.angle)
        n_ticks = self.options.n_ticks
        n_subticks = self.options.n_subticks
        ticks_delta = angle / (n_ticks - 1)
        subticks_delta = ticks_delta / (n_subticks + 1)
        subtick_angles = []
        for tick_angle in self.get_tick_angles()[:-1]:
            for subtick in range(n_subticks):
                subtick_angles.append(tick_angle + subticks_delta * (subtick + 1))
        return subtick_angles

    def effect(self):

        parent = self.svg.get_current_layer()
        radius = self.svg.unittouu(str(self.options.radius) + self.options.units)
        self.x_offset = self.svg.unittouu(str(self.options.x) + self.options.units)
        self.y_offset = self.svg.unittouu(str(self.options.y) + self.options.units)
        angle = self.options.angle*pi/180.0
        is_outer = True
        if self.options.style == 'marks_inwards':
            is_outer = False

        tick_length = self.svg.unittouu(str(self.options.ticksize) + self.options.units)
        subtick_length = self.svg.unittouu(str(self.options.subticksize) + self.options.units)
        arc_radius = radius

        # Labeling settings
        text_spacing = self.svg.unittouu(str(self.options.text_offset) + self.options.units)
        text_size = self.svg.unittouu(str(self.options.text_size) + self.options.units)

        if not is_outer:
            subtick_radius = radius + tick_length - subtick_length
            arc_radius = radius + tick_length
        else:
            subtick_radius = radius
            arc_radius = radius

        if self.options.draw_arc:
            self.draw_knob_arc(arc_radius, parent, angle)

        if self.options.draw_centering_circle:
            self.draw_centering_circle(arc_radius + tick_length + text_size + text_spacing, parent)

        # Draw main ticks        
        tick_angles = self.get_tick_angles()
        for angle in tick_angles:
            self.draw_tick(radius, angle, tick_length, parent)

        if self.options.labels_enabled:
            labels = self.get_tick_labels()
            label_radius = radius + tick_length + text_spacing
            for angle, label in zip(tick_angles, labels):
                self.draw_text(label, label_radius, angle, text_size, parent)

        # Draw subticks
        for angle in self.get_subtick_angles():
            self.draw_tick(subtick_radius, angle, subtick_length, parent)

if __name__ == '__main__':
    e = Knob_Scale()
    e.run()

