# -*- coding: utf-8 -*-

"""
Is my mongo exposed?
"""
import os
import sys
import urwid
from widgets import *
from cards import *
from palette import palette
from tools import check_version


class App(object):

    def __init__(self):
        self.name = 'mongoaudit'
        self.version = '0.0.1'
        get_latest = check_version(self.version)
        self.cards = Cards(self)
        self.setup_view()
        self.main()

    def setup_view(self):
        placeholder = urwid.SolidFill()
        self.loop = urwid.MainLoop(
            placeholder, palette, unhandled_input=self.key_handler)
        self.loop.widget = urwid.AttrMap(placeholder, 'bg')
        self.loop.widget._command_map['tab'] = 'cursor down'
        self.loop.widget._command_map['shift tab'] = 'cursor up'
        self.loop.screen.set_terminal_properties(colors=256)
        self.cards.welcome()

    def render(self, card):
        div = urwid.Divider()
        rdiv = urwid.AttrMap(div, 'header')
        header = urwid.Filler(urwid.Pile(
            [rdiv, rdiv, rdiv, rdiv, rdiv]), valign='top')
        h1 = urwid.Text(('h1', self.name))
        h2 = urwid.Text(('h2', 'v' + self.version), align='right')
        hg = urwid.AttrMap(urwid.Padding(urwid.Columns(
            [h1, h2]), left=2, right=2, align='center'), 'header')
        body = urwid.Pile([hg, rdiv, card, div])
        w = urwid.Overlay(body, header, 'center', 76, 'top', 'pack', top=1)
        self.loop.widget.original_widget = w

    def key_handler(self, key):
        if key in ('q', 'Q', 'esc'):
            raise urwid.ExitMainLoop()
        elif key == 'ctrl r':
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def main(self):
        self.loop.run()


def main():
    App().main()

if __name__ == '__main__':
    main()
