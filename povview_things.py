#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  povview_things.py
#
#  Copyright 2024 John Coppens <john@jcoppens.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')
from gi.repository import Gtk, GooCanvas

from math import cos, sin, pi

SUBDIV = 12

class ThreeD_object:
    def __init__(self):
        pass

class Vec3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

class RGB:
    def __init__(self, r, g = None, b = None):
        if isinstance(r, list):
            self._rgb = r
        else:
            self._rgb = [r, g, b]

    def __str__(self):
        return f"r: {self._rgb[0]}, g: {self._rgb[1]}, b: {self._rgb[2]}"

    @property
    def r(self):
        return self._rgb[0]

    @property
    def g(self):
        return self._rgb[1]

    @property
    def b(self):
        return self._rgb[2]

    @property
    def rgb(self):
        return self._rgb

class Cone(ThreeD_object):
    """ tc      self.tc     vec3    Cone top center
        tr      self.tr     float   Cone top radius
        bc      self.bc     vec3    Cone bottom center
        br      self.br     float   Cone bottom radius
    """
    def __init__(self, cone_par):
        self.tc = cone_par[0]
        self.tr = cone_par[1]
        self.bc = cone_par[2]
        self.br = cone_par[3]
        self.create_wireframe()

    def __str__(self):
        return (f'Cone:\n'
                f'top:    {self.tc[0]:10g}, {self.tc[1]:10g}, {self.tc[2]:10g}'
                f' radius: {self.tr:10g}\n'
                f'bottom: {self.bc[0]:10g}, {self.bc[1]:10g}, {self.bc[2]:10g}'
                f' radius: {self.br:10g}\n')

    def create_wireframe(self):
        self.tx = []
        self.ty = []
        self.tz = []
        self.bx = []
        self.by = []
        self.bz = []
        dsub = 2 * pi / SUBDIV

        for i in range(SUBDIV):
            self.tx += [self.tc[0] + self.tr * cos(dsub * i)]
            self.ty += [-self.tc[1]]
            self.tz += [self.tc[2] + self.tr * sin(dsub * i)]

            self.bx += [self.bc[0] + self.br * cos(dsub * i)]
            self.by += [-self.bc[1]]
            self.bz += [self.bc[2] + self.br * sin(dsub * i)]

    def to_svg(self, side):
        svg = ""
        if side == 'xy':
            svg += f"M{self.tx[0]:g},{self.ty[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.tx[s]:g},{self.ty[s]:g} "
            svg += 'Z '

            svg += f"M{self.bx[0]:g},{self.by[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.bx[s]:g},{self.by[s]:g} "
            svg += 'Z '

            for s in range(SUBDIV):
                svg += (f"M{self.tx[s]:g},{self.ty[s]:g} "
                        f"L{self.bx[s]:g},{self.by[s]:g} ")

        elif side == 'yz':
            svg += f"M{self.tz[0]:g},{self.ty[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.tz[s]:g},{self.ty[s]:g} "
            svg += 'Z '

            svg += f"M{self.bz[0]:g},{self.by[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.bz[s]:g},{self.by[s]:g} "
            svg += 'Z '

            for s in range(SUBDIV):
                svg += (f"M{self.tz[s]:g},{self.ty[s]:g} "
                        f"L{self.bz[s]:g},{self.by[s]:g} ")

        else:  # zx
            svg += f"M{self.tx[0]:g},{self.tz[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.tx[s]:g},{self.tz[s]:g} "
            svg += 'Z '

            svg += f"M{self.bx[0]:g},{self.bz[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.bx[s]:g},{self.bz[s]:g} "
            svg += 'Z '

            for s in range(SUBDIV):
                svg += (f"M{self.tx[s]:g},{self.tz[s]:g} "
                        f"L{self.bx[s]:g},{self.bz[s]:g} ")

        return svg

    def draw_on(self, views):
        for view in ['xy', 'yz', 'zx']:
            root = views[view]['canvas'].get_root_item()
            GooCanvas.CanvasPath(
                        parent=root,
                        data=self.to_svg(view),
                        line_width=1,
                        stroke_color='Blue',
                        fill_color=None)

class Box(ThreeD_object):
    def __init__(self, box_par):
        # box_par debe contener las dos esquinas opuestas del box
        self.corner1 = box_par[0]  # Primer vértice del box (vector 3D)
        self.corner2 = box_par[1]  # Segundo vértice opuesto del box (vector 3D)
        self.create_wireframe()

    def __str__(self):
        return (f'Box:\n'
                f'corner1: {self.corner1[0]:10g}, {self.corner1[1]:10g}, {self.corner1[2]:10g}\n'
                f'corner2: {self.corner2[0]:10g}, {self.corner2[1]:10g}, {self.corner2[2]:10g}\n')

    def create_wireframe(self):
        x_min, y_min, z_min = min(self.corner1[0], self.corner2[0]), min(self.corner1[1], self.corner2[1]), min(self.corner1[2], self.corner2[2])
        x_max, y_max, z_max = max(self.corner1[0], self.corner2[0]), max(self.corner1[1], self.corner2[1]), max(self.corner1[2], self.corner2[2])

        self.vertices = [
            [x_min, y_min, z_min], [x_max, y_min, z_min], [x_max, y_max, z_min], [x_min, y_max, z_min],
            [x_min, y_min, z_max], [x_max, y_min, z_max], [x_max, y_max, z_max], [x_min, y_max, z_max]
        ]

    def to_svg(self, side):
        svg = ""
        
        if side == 'xy':
            # Base (z_min)
            svg += f"M{self.vertices[0][0]},{self.vertices[0][1]} "
            for i in range(1, 4):
                svg += f"L{self.vertices[i][0]},{self.vertices[i][1]} "
            svg += f"L{self.vertices[0][0]},{self.vertices[0][1]} "  # Cierra el contorno de la base

            # Tapa (z_max)
            svg += f"M{self.vertices[4][0]},{self.vertices[4][1]} "
            for i in range(5, 8):
                svg += f"L{self.vertices[i][0]},{self.vertices[i][1]} "
            svg += f"L{self.vertices[4][0]},{self.vertices[4][1]} "  # Cierra el contorno de la tapa

            # Conexiones entre la base y la tapa
            for i in range(4):
                svg += f"M{self.vertices[i][0]},{self.vertices[i][1]} L{self.vertices[i+4][0]},{self.vertices[i+4][1]} "

        elif side == 'yz':
            # Base (x_min)
            svg += f"M{self.vertices[0][2]},{self.vertices[0][1]} "
            for i in range(1, 4):
                svg += f"L{self.vertices[i][2]},{self.vertices[i][1]} "
            svg += f"L{self.vertices[0][2]},{self.vertices[0][1]} "  # Cierra el contorno de la base

            # Tapa (x_max)
            svg += f"M{self.vertices[4][2]},{self.vertices[4][1]} "
            for i in range(5, 8):
                svg += f"L{self.vertices[i][2]},{self.vertices[i][1]} "
            svg += f"L{self.vertices[4][2]},{self.vertices[4][1]} "  # Cierra el contorno de la tapa

            # Conexiones entre la base y la tapa
            for i in range(4):
                svg += f"M{self.vertices[i][2]},{self.vertices[i][1]} L{self.vertices[i+4][2]},{self.vertices[i+4][1]} "

        else:  # zx
            # Base (y_min)
            svg += f"M{self.vertices[0][0]},{self.vertices[0][2]} "
            for i in range(1, 4):
                svg += f"L{self.vertices[i][0]},{self.vertices[i][2]} "
            svg += f"L{self.vertices[0][0]},{self.vertices[0][2]} "  # Cierra el contorno de la base

            # Tapa (y_max)
            svg += f"M{self.vertices[4][0]},{self.vertices[4][2]} "
            for i in range(5, 8):
                svg += f"L{self.vertices[i][0]},{self.vertices[i][2]} "
            svg += f"L{self.vertices[4][0]},{self.vertices[4][2]} "  # Cierra el contorno de la tapa

            # Conexiones entre la base y la tapa
            for i in range(4):
                svg += f"M{self.vertices[i][0]},{self.vertices[i][2]} L{self.vertices[i+4][0]},{self.vertices[i+4][2]} "

        return svg

    def draw_on(self, views):
        for view in ['xy', 'yz', 'zx']:
            root = views[view]['canvas'].get_root_item()
            GooCanvas.CanvasPath(
                parent=root,
                data=self.to_svg(view),
                line_width=1,
                stroke_color='Red',
                fill_color=None)
