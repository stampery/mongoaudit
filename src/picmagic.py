# -*- coding: utf-8 -*-
import os
import sys

import urwid




def pixel_process(color):
    return (urwid.AttrSpec(color, color, 256), ' ')


def round_compo(compo):
    return hex(ord(compo))[2]

def read(path, align='left'):
    def line_process(line):
        return urwid.AttrMap(urwid.Text(map(pixel_process, line), wrap='clip', align=align), 'pic')

    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    with open(os.path.join(base_path, 'rsc/' + path), 'r') as file_to_read:
        bytes_read = file_to_read.read()

    img_size = {"width":ord(bytes_read[18]), "height":ord(bytes_read[22])}

    bmp = {"complete": len(bytes_read),
           "content": img_size["width"] * img_size["height"] * 3,
           "line_size": img_size["width"] * 3}

    pic = []
    for i in range(bmp["complete"] -  bmp["content"], bmp["complete"], bmp["line_size"]):
        raw_line = bytes_read[i:i + bmp["line_size"]]
        row = []
        for j in range(0, bmp["line_size"], 3):
            raw_pixel = raw_line[j:j + 3][::-1]
            color = '#' + ''.join(map(round_compo, raw_pixel))
            row.append(color)
        pic.append(row)
    return urwid.Pile(map(line_process, pic[::-1]))
