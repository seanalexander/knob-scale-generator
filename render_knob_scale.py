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
        self.arg_parser.add_argument("--logarithmic_ticks",
                        type=inkex.Boolean,
                        dest="logarithmic_ticks",
                        default="False",
                        help="Whether to space ticks according to a log scale.")
        self.arg_parser.add_argument("--logarithmic_subticks",
                        type=inkex.Boolean,
                        dest="logarithmic_subticks",
                        default="False",
                        help="Whether to space ticks according to a log scale. " \
                             "Using this without the log-scale ticks will make " \
                             "an exponential scale.")

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

        self.arg_parser.add_argument("--numbering_position",
                             type=str,
                             dest="numbering_position", default="bottom",
                             help="Starting position for numbering (top, middle, bottom)")
        self.arg_parser.add_argument("--custom_start_degree",
                                    type=float,
                                    dest="custom_start_degree", default=0.0,
                                    help="Custom degree start position (Overrides numbering position)")

        self.arg_parser.add_argument("--draw_circles",
                                    type=inkex.Boolean,
                                    dest="draw_circles", default='True',
                                    help="Whether to draw circles or not")

        self.arg_parser.add_argument("--skip_mark_at_gap",
                                    type=inkex.Boolean,
                                    dest="skip_mark_at_gap",
                                    default='False',
                                    help="Skip the mark at the gap position.")

    def draw_knob_arc(self, radius, parent, transform=''):
        # Determine the start point angle based on custom start degree or numbering position
        start_point_angle = self.get_start_angle()

        # Calculate the end point angle based on the arc angle
        total_angle = radians(self.options.angle)
        end_point_angle = start_point_angle + total_angle

        # Convert all necessary values to strings
        style = {
            'stroke': '#000000',
            'stroke-width': str(self.options.linewidth),
            'fill': 'none'
        }

        ell_attribs = {
            'style': str(inkex.Style(style)),
            inkex.addNS('cx', 'sodipodi'): str(self.x_offset),         # Convert to string
            inkex.addNS('cy', 'sodipodi'): str(self.y_offset),         # Convert to string
            inkex.addNS('rx', 'sodipodi'): str(radius),                # Convert to string
            inkex.addNS('ry', 'sodipodi'): str(radius),                # Convert to string
            inkex.addNS('start', 'sodipodi'): str(float(start_point_angle)),  # Explicit float to string
            inkex.addNS('end', 'sodipodi'): str(float(end_point_angle)),      # Explicit float to string
            inkex.addNS('open', 'sodipodi'): 'true',                   # Open arc to leave a gap
            inkex.addNS('type', 'sodipodi'): 'arc',
            'transform': str(transform)  # Ensure transform is a string
        }

        # Create the arc element in the parent SVG element
        etree.SubElement(parent, inkex.addNS('path', 'svg'), ell_attribs)


    def get_start_angle(self):
        # Use custom start degree if set
        if self.options.custom_start_degree != 0.0:
            return radians(self.options.custom_start_degree)
        
        # Otherwise, use the numbering position
        return self.get_numbering_position_angle()


    def get_numbering_position_angle(self):
        # Returns the appropriate start angle for the numbering position
        if self.options.numbering_position == "top":
            return pi / 2  # Top (90 degrees)
        elif self.options.numbering_position == "left":
            return pi  # Left (180 degrees)
        elif self.options.numbering_position == "right":
            return 0  # Right (0 degrees)
        elif self.options.numbering_position == "bottom":
            return -pi / 2  # Bottom (270 degrees)
        else:
            # Default to top (90 degrees)
            return pi / 2



    def get_gap_angle(self):
        # Calculate the gap angle based on the custom start degree or numbering position
        if self.options.custom_start_degree != 0.0:
            # Use custom start degree if set
            return radians(self.options.custom_start_degree)
        else:
            # Use the numbering position if custom start degree is not set
            return self.get_numbering_position_angle()

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
        # Check if the circle should be skipped at the gap
        gap_angle = self.get_gap_angle()  # This calculates the angle where the gap is

        if self.options.skip_mark_at_gap and abs(mark_angle - gap_angle) < 0.01:  # Small tolerance to check for gap
            return  # Skip drawing the circle if it's at the gap

        # Continue with drawing the circle
        cx = x_offset + radius * cos(mark_angle)
        cy = y_offset + radius * sin(mark_angle)
        r = mark_length / 2.0

        style = {
            'stroke': '#000000',
            'stroke-width': '0',
            'fill': '#000000'
        }

        circ_attribs = {
            'style': str(inkex.Style(style)),
            'cx': str(cx),
            'cy': str(cy),
            'r': str(r)
        }

        circle = etree.SubElement(parent, inkex.addNS('circle', 'svg'), circ_attribs)


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
        # Check if the mark should be skipped at the gap
        gap_angle = self.get_gap_angle()

        if self.options.skip_mark_at_gap and abs(mark_angle - gap_angle) < 0.01:  # Small tolerance to check for gap
            return  # Skip drawing the mark if it's at the gap

        # Continue with the usual drawing logic for ticks (marks)
        if self.options.style == 'marks_inwards':
            self.draw_knob_line_mark(self.x_offset, self.y_offset, radius + mark_size, mark_angle, -mark_size, parent)
        elif self.options.style == 'marks_outwards':
            self.draw_knob_line_mark(self.x_offset, self.y_offset, radius, mark_angle, mark_size, parent)
        elif self.options.style == 'marks_circles' and self.options.draw_circles:
            self.draw_circle_mark(self.x_offset, self.y_offset, radius, mark_angle, mark_size, parent)

    def get_tick_angles(self):
        n_ticks = self.options.n_ticks
        if n_ticks <= 0:
            return []

        angle = radians(self.options.angle)

        # Use custom degree if set, otherwise default to numbering position
        if self.options.custom_start_degree != 0.0:
            start_angle = radians(self.options.custom_start_degree)
        else:
            if self.options.numbering_position == "top":
                start_angle = pi / 2 - 0.5 * angle
            elif self.options.numbering_position == "middle":
                start_angle = 0 - 0.5 * angle
            else:  # default to bottom
                start_angle = 1.5 * pi - 0.5 * angle

        if self.options.logarithmic_ticks:
            tick_angles = []
            for i in range(n_ticks):
                tick_angle = start_angle + angle * log(i+1) / log(n_ticks)
                tick_angles.append(tick_angle)
            return tick_angles
        else:
            ticks_delta = angle / (n_ticks - 1)
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
        if self.options.n_ticks < 2:
            return []
        
        n_ticks = self.options.n_ticks
        n_subticks = self.options.n_subticks
        angle = radians(self.options.angle)
        start_angle = 1.5*pi - 0.5*angle
        
        subtick_angles = []
        tick_angles = self.get_tick_angles()
        for tick, cur_tick_angle in enumerate(tick_angles[:-1]):
            next_tick_angle = tick_angles[tick+1]
            tick_delta = next_tick_angle - cur_tick_angle
            if self.options.logarithmic_ticks:
                for i in range(n_subticks):
                    fraction = (i+1) / (n_subticks+1) + tick
                    fraction = log(fraction+1) / log(n_ticks)
                    subtick_angles.append(start_angle + angle * fraction)
            elif self.options.logarithmic_subticks:
                for i in range(n_subticks):
                    fraction = log(i+2) / log(n_subticks+2)
                    subtick_angles.append(cur_tick_angle + tick_delta * fraction)
            else: # linear
                for i in range(n_subticks):
                    fraction = (i + 1) / (n_subticks + 1)
                    subtick_angles.append(cur_tick_angle + tick_delta * fraction)
        return subtick_angles

    def update_custom_start_degree_based_on_numbering_position(self):
        # If the numbering position is changed, set the custom start degree accordingly
        if self.options.custom_start_degree == 0.0:
            if self.options.numbering_position == "top":
                self.options.custom_start_degree = 90  # Top corresponds to 90 degrees
            elif self.options.numbering_position == "left":
                self.options.custom_start_degree = 180  # Left corresponds to 180 degrees
            elif self.options.numbering_position == "right":
                self.options.custom_start_degree = 0  # Right corresponds to 0 degrees
            elif self.options.numbering_position == "bottom":
                self.options.custom_start_degree = 270  # Bottom corresponds to 270 degrees


    def effect(self):

        self.update_custom_start_degree_based_on_numbering_position()

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
        for tick_angle in tick_angles:
            self.draw_tick(radius, tick_angle, tick_length, parent)

        # Draw subticks
        for subtick_angle in self.get_subtick_angles():
            self.draw_tick(subtick_radius, subtick_angle, subtick_length, parent)

        if self.options.labels_enabled:
            labels = self.get_tick_labels()
            label_radius = radius + tick_length + text_spacing
            for angle, label in zip(tick_angles, labels):
                self.draw_text(label, label_radius, angle, text_size, parent)


if __name__ == '__main__':
    e = Knob_Scale()
    e.run()

