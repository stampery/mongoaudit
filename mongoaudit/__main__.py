# -*- coding: utf-8 -*-

"""
Is my mongo exposed?
"""
import os
import sys
import urwid
from .version import __version__
from .cards import Cards
from .palette import PALETTE
from .tools import check_version


class App(object):
    def __init__(self):
        self.name = 'mongoaudit'
        self.version = __version__
        check_version(self.version)
        urwid.set_encoding("UTF-8")
        self.cards = Cards(self)
        self.setup_view()
        self.main()

    def setup_view(self):
        placeholder = urwid.SolidFill()
        self.loop = urwid.MainLoop(
            placeholder, PALETTE, unhandled_input=self.key_handler)
        self.loop.widget = urwid.AttrMap(placeholder, 'bg')
        #self.loop.widget._command_map['tab'] = 'cursor down'
        #self.loop.widget._command_map['shift tab'] = 'cursor up'
        self.loop.screen.set_terminal_properties(colors=256)
        self.cards.welcome()

    def render(self, card):
        div = urwid.Divider()
        rdiv = urwid.AttrMap(div, 'header')
        header = urwid.Filler(urwid.Pile(
            [rdiv, rdiv, rdiv, rdiv, rdiv]), valign='top')
        h1_text = urwid.Text(('h1', self.name))
        h2_text = urwid.Text(('h2', 'v' + self.version), align='right')
        hg_text = urwid.AttrMap(urwid.Padding(urwid.Columns(
            [h1_text, h2_text]), left=2, right=2, align='center'), 'header')
        body = urwid.Pile([hg_text, rdiv, card, div])
        widget = urwid.Overlay(body, header, 'center', 76, 'top', 'pack', top=1)
        self.loop.widget.original_widget = widget

    @staticmethod
    def key_handler(key):
        if key in ('q', 'Q', 'esc'):
            raise urwid.ExitMainLoop()
        elif key == 'ctrl r':
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def main(self):
        try:
            self.loop.run()
        except KeyboardInterrupt:
            return 0


def main():
    App().main()


if __name__ == "__main__":
    main()
