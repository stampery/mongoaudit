# -*- coding: utf-8 -*-

import urwid
from picmagic import read as picRead
from tools import validate_uri
from widgets import *
from testers import *

class Cards(object):

  def __init__(self, app):
    self.app = app

  def welcome(self):
    pic = picRead('../rsc/welcome.bmp', align='right')
    text = urwid.Text((
        'text',
        '%s is a CLI tool for auditing MongoDB servers, detecting poor security settings and performing automated penetration testing.'
        % self.app.name))
    button = urwid.AttrMap(
        TextButton(
            'Start', on_press=self.choose_test), 'button')
    card = Card(text, header=pic, footer=button)
    self.app.render(card)

  def choose_test(self, button=None):
    txt = urwid.Text(
        '%s provides two distinct types of test suites covering  security in different depth. Please choose which tests you want to run:'
        % self.app.name)

    basic = ImageButton(
        picRead('../rsc/%s' % 'bars_min.bmp'),
        [('text bold', 'Basic'),
         ('text', 'Analize server perimeter security. (Does not require valid credentials)')])
    exhaustive = ImageButton(
        picRead('../rsc/%s' % 'bars_max.bmp'),
        [('text bold', 'Exhaustive'),
         ('text', 'Connect to MongoDB server and analize security from inside. (Requires valid credentials)')])
    content = urwid.Pile([txt, div, basic, exhaustive])
    urwid.connect_signal(basic, 'click', self.basic_test)
    urwid.connect_signal(exhaustive, 'click', self.exhaustive_test)
    card = Card(content)
    self.app.render(card)

  def basic_test(self, _):
    intro = urwid.Text('Please provide the url for the')
    fields = ['URI']
    validate = lambda form, uri: validate_uri(uri, form, "Invalid URI", self.run_basic)
    form = FormCard(intro, fields, 'Run Test', validate, back=self.choose_test)

    self.app.render(form)

  def exhaustive_test(self, _):
    content = urwid.Pile([
      urwid.Text(('text bold', 'Exhaustive Test')),
      div,
      urwid.Text(('text', 'Please enter your MongoDB URI')),
      urwid.Text(('text italic', '(mongodb://user:password@domain.tld:port/database)'))
    ])

    validate = lambda form, mongodb_uri: validate_uri(mongodb_uri, form, "Invalid Mongo URI", self.run_exhaustive)
    self.app.render(FormCard(content,["MongoDB URI"], "Run exhaustive test", validate, back=self.choose_test))

  def run_basic(self, uri):
    card = Card(urwid.Text("working \n" + str(uri)))
    self.app.render(card)

  def run_exhaustive(self, uri):
    card = Card(urwid.Text("working \n" + str(uri)))
    self.app.render(card)
