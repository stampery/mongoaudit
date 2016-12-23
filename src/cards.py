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
            '%s is a CLI tool for auditing MongoDB servers, detecting poor security \
            settings and performing automated penetration testing.'
            % self.app.name))
        button = urwid.AttrMap(
            TextButton(
                'Start', on_press=self.choose_test), 'button')
        
        #debug
        # debug = urwid.AttrMap(
        #     TextButton(
        #         'Debug', align='left', on_press=self.email_prompt), 'button')
        # button = urwid.Columns([debug, button]) #debug
        card = Card(text, header=pic, footer=button)
        self.app.render(card)

    def choose_test(self, button=None):
        txt = urwid.Text([('text bold', self.app.name),
                          ' provides two distinct types of test suites covering  \
                          security in different depth. Please choose which tests \
                          you want to run:'])

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
        urwid.connect_signal(
            basic, 'click', lambda _: self.uri_prompt(**basic_args))
        advanced_args = {'title': 'Advanced', 'label': 'Please enter your MongoDB URI',
                         'uri_example': 'mongodb://user:password@domain.tld:port/database',
                         'uri_error': "Invalid MongoDB URI", 'tests': basic_tests + advanced_tests}
        urwid.connect_signal(
            advanced, 'click', lambda _: self.uri_prompt(**advanced_args))
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
            urwid.Text([label + ' (', ('text italic', uri_example), ')'])
        ])
        validate = lambda form, uri: validate_uri(
            uri, form, uri_error, lambda cred: self.run_test(cred, title, tests))
        form = FormCard(intro, ['URI'], 'Run ' + title.lower() +
                        ' test', validate, back=self.choose_test)
        self.app.render(form)

    def run_test(self, cred, title, tests):
        """
        Args:
          cred (dict(str: str)): credentials
          title (str): title for the TestRunner
          tests (Test[]): test to run
        """
        test_runner = TestRunner(
            title, cred, tests, self.app, self.display_overview)
        # the name of the bmp is composed with the title
        pic = picRead('rsc/check_' + title.lower() + '.bmp', align='right')

        footer = urwid.AttrMap(TextButton(
            'Cancel', align='left', on_press=self.choose_test), 'button')
        card = Card(test_runner, header=pic, footer=footer)
        self.app.render(card)
        test_runner.run()

    def display_overview(self, result):
        """
        Args:
            result (dict()): the result returned by test_runner
        """
        def reduce_result(res, values):
            if not bool(values):
                return []
            return reduce_result(res % values[-1], values[:-1]) + [res / values[-1]]

        base = len(result) + 1
        # range 4 because the possible values for result  are [False, True,
        # 'custom', 'ommited']
        values = [base**x for x in range(4)]
        total = reduce(lambda x, y: x + values[y['result']], result, 0)
        header = urwid.Text(('header red', 'Result overview'))
        subtitle = urwid.Text(
            ('text', 'Finished running ' + str(len(result)) + " tests."))
        overview = reduce_result(total, values)
        overview = urwid.Text([('ok', str(overview[1])), ('text', ' passed   '),
                               ('error', str(overview[0])
                                ), ('text', ' failed   '),
                               ('warning', str(overview[2])
                                ), ('text', ' warning   '),
                               ('info', str(overview[3])), ('text', ' ommited')])
        footer = urwid.AttrMap(TextButton(
            '< Back to main menu', align='left', on_press=self.choose_test), 'button')

        results_button = LineButton([('text', 'View detailed results')])
        email_button = LineButton([('text', 'Email')])

        urwid.connect_signal(
            results_button, 'click', lambda _: self.display_test_result(result))
        urwid.connect_signal(
            email_button, 'click', lambda _: self.email_prompt(result))

        card = Card(urwid.Pile([header, div, subtitle, div, overview, div,
                                results_button, email_button]), footer=footer)
        self.app.render(card)

    def display_test_result(self, result):
        display_test = DisplayTest(result)
        footer = urwid.AttrMap(TextButton('< Back to result overview', align='left', on_press=(
            lambda _: self.display_overview(result))), 'button')
        card = Card(display_test, footer=footer)
        self.app.render(card)

    def email_prompt(self, result):
        header = urwid.Text(('header red', 'Email result'))
        subtitle = urwid.Text(('text','The quick brown fox jumps over the lazy dog'))
        content = urwid.Pile([header, div, subtitle])
        card = FormCard(content, ['Email'], 'Send', None, lambda _: self.display_overview(result))
        self.app.render(card)
