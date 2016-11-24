# -*- coding: utf-8 -*-

"""
Is my mongo exposed?
"""

import urwid
from widgets import *
from cards import *
from palette import palette

class App(object):

    def __init__(self):
        self.name = 'mongo-audit'
        self.version = '0.0.1'
        self.cards = Cards(self)
        self.setup_view()
        self.main()

    def setup_view(self):
        placeholder = urwid.SolidFill()
        self.loop = urwid.MainLoop(placeholder, palette, unhandled_input=self.key_handler)
        self.loop.widget = urwid.AttrMap(placeholder, 'bg')
        self.loop.screen.set_terminal_properties(colors=256)
        self.cards.welcome()

    def render(self, card):
        div = urwid.Divider()
        rdiv = urwid.AttrMap(div, 'header')
        header = urwid.Filler(urwid.Pile([rdiv, rdiv, rdiv, rdiv, rdiv]), valign='top')
        h1 = urwid.Text(('h1', self.name))
        h2 = urwid.Text(('h2', 'v'+self.version), align='right')
        hg = urwid.AttrMap(urwid.Padding(urwid.Columns([h1, h2]), left=2, right=2, align='center'), 'header')
        copy = pad(urwid.Text(('copy', '© 2016 Stampery, Inc. Available under MIT License.')))
        body = urwid.Pile([hg, rdiv, card, div, copy])
        w = urwid.Overlay(body, header, 'center', 76, 'top', 'pack', top=1)
        self.loop.widget.original_widget = w

    def key_handler(self, key):
        if key in ('q', 'Q', 'esc'):
            raise urwid.ExitMainLoop()

    def main(self):
        self.loop.run()

def main():
    App().main()

if __name__ == '__main__':
    main()
