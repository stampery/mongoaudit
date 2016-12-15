# -*- coding: utf-8 -*-
import urwid
from picmagic import read as picRead
from tools import validate_uri
from widgets import *
from testers import *

class Cards(object):
  credentials = []

  def __init__(self, app):
    self.app = app

  def welcome(self):
    pic = picRead('rsc/welcome.bmp', align='right')
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
    txt = urwid.Text([('text bold', self.app.name),
        ' provides two distinct types of test suites covering  security in different depth. Please choose which tests you want to run:'])

    basic = ImageButton(
        picRead('rsc/%s' % 'bars_min.bmp'),
        [('text bold', 'Basic'),
         ('text', 'Analize server perimeter security. (Does not require valid credentials)')])
    advanced = ImageButton(
        picRead('rsc/%s' % 'bars_max.bmp'),
        [('text bold', 'Advanced'),
         ('text', 'Connect to MongoDB server and analize security from inside. (Requires valid credentials)')])
    content = urwid.Pile([txt, div, basic, advanced])

    basic_args = {'title': 'Basic', 'label': 'Please provide the URI of your MongoDB server', 'uri_example': 'domain.tld:port',
                   'uri_error': "Invalid URI", 'tests': basic_tests}
    urwid.connect_signal(basic, 'click', lambda _: self.uri_prompt(**basic_args))
    advanced_args = {'title': 'Advanced', 'label': 'Please enter your MongoDB URI', 'uri_example': 'mongodb://user:password@domain.tld:port/database',
                   'uri_error': "Invalid MongoDB URI", 'tests': basic_tests + advanced_tests}
    urwid.connect_signal(advanced, 'click',lambda _: self.uri_prompt(**advanced_args))
    card = Card(content)
    self.app.render(card)

  def uri_prompt(self, title, label, uri_example, uri_error, tests):
    """
    Args:
      title (str): Title for the test page
      label (str): label for the input field
      uri_example (str): example of a valid URI
      uri_error (str): error to display if URI is not valid
      tests (Test[]): test to pass as argument to run_test
    """
    intro = urwid.Pile([
      urwid.Text(('text bold', title + ' test')),
      div,
      urwid.Text([label + ' (',('text italic', uri_example), ')'])
    ])
    validate = lambda form, uri: validate_uri(uri, form, uri_error, lambda cred: self.run_test(cred, title, tests))
    form = FormCard(intro, ['URI'], 'Run ' + title.lower() +' test', validate, back=self.choose_test)
    self.app.render(form)

  def run_test(self, cred, title, tests):
    """
    Args:
      cred (dict(str: str)): credentials
      title (str): title for the TestRunner
      tests (Test[]): test to run
    """
    test_runner = TestRunner(title, cred, tests, self.app, self.display_results)
    # the name of the bmp is composed with the title
    pic = picRead('rsc/check_' + title.lower() + '.bmp', align='right')

    footer = urwid.AttrMap(TextButton('Cancel', align='left', on_press=self.choose_test),'button')
    card = Card(test_runner, header=pic, footer=footer)
    self.app.render(card)
    test_runner.run()

  def display_results(self, title, list_walker, total):
    """
    Args:
      title (str): title used when displaying the results
      list_walker (urwid.SimpleListWalker): content to display in a ListBox
      total (int) : number of test finished
    """
    intro = urwid.Text(('text bold',title + ' test results'))
    footer = urwid.AttrMap(TextButton('Back', align='left', on_press=self.choose_test),'button')
    lbox = urwid.BoxAdapter(urwid.ListBox(list_walker), height=12)
    pile = urwid.Pile([intro, div, lbox, div, total])
    card = Card(pile, footer=footer)
    self.app.render(card)
