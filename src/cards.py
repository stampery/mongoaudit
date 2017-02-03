# -*- coding: utf-8 -*-
from functools import reduce

from picmagic import read as picRead
from tools import validate_uri, send_result, load_test, validate_email
from widgets import *


class Cards(object):
    def __init__(self, app):
        self.app = app
        self.tests = load_test('tests.json')

    def welcome(self):
        pic = picRead('welcome.bmp', align='right')
        text = urwid.Text(
            ('text',
             '%s is a CLI tool for auditing MongoDB servers, detecting poor security settings and performing automated penetration testing.' %
             self.app.name))
        button = urwid.AttrMap(
            TextButton(
                'Start', on_press=self.choose_test), 'button')

        card = Card(text, header=pic, footer=button)
        self.app.render(card)

    def choose_test(self, button=None):
        txt = urwid.Text(
            [
                ('text bold',
                 self.app.name),
                ' provides two distinct types of test suites covering security in different depth. Please choose which tests you want to run:'])

        basic = ImageButton(
            picRead('bars_min.bmp'),
            [('text bold', 'Basic'),
             ('text', 'Analize server perimeter security. (Does not require valid credentials)')])
        advanced = ImageButton(
            picRead('bars_max.bmp'),
            [('text bold', 'Advanced'),
             ('text', 'Connect to MongoDB server and analize security from inside. (Requires valid credentials)')])
        content = urwid.Pile([txt, DIV, basic, advanced])

        basic_args = {
            'title': 'Basic',
            'label': 'Please provide the URI of your MongoDB server',
            'uri_example': 'domain.tld:port',
            'tests': self.tests['basic']}
        urwid.connect_signal(
            basic, 'click', lambda _: self.uri_prompt(**basic_args))
        advanced_args = {
            'title': 'Advanced',
            'label': 'Please enter your MongoDB URI',
            'uri_example': 'mongodb://user:password@domain.tld:port/database',
            'tests': self.tests['basic'] + self.tests['advanced']}
        urwid.connect_signal(
            advanced, 'click', lambda _: self.uri_prompt(**advanced_args))
        card = Card(content)
        self.app.render(card)

    def uri_prompt(self, title, label, uri_example, tests):
        """
        Args:
          title (str): Title for the test page
          label (str): label for the input field
          uri_example (str): example of a valid URI
          tests (Test[]): test to pass as argument to run_test
        """
        intro = urwid.Pile([
            urwid.Text(('text bold', title + ' test')),
            DIV,
            urwid.Text([label + ' (', ('text italic', uri_example), ')'])
        ])
        validate = lambda form, uri: validate_uri(
            uri, form, lambda cred: self.run_test(
                cred, title, tests))
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
        pic = picRead('check_' + title.lower() + '.bmp', align='right')

        footer = self.get_footer('Cancel', self.choose_test)
        card = Card(test_runner, header=pic, footer=footer)
        self.app.render(card)
        test_runner.run()

    def display_overview(self, result, title, urn):
        """
        Args:
            result (dict()): the result returned by test_runner
        """

        def reduce_result(res, values):
            if not bool(values):
                return []
            return reduce_result(res %
                                 values[-1], values[:-1]) + [res / values[-1]]

        base = len(result) + 1
        # range 4 because the possible values for result  are [False, True,
        # 'custom', 'ommited']
        values = [base ** x for x in range(4)]
        total = reduce(lambda x, y: x + values[y['result']], result, 0)
        header = urwid.Text(('header red', 'Result overview'))
        subtitle = urwid.Text(
            ('text', 'Finished running ' + str(len(result)) + " tests."))
        overview = reduce_result(total, values)
        overview = urwid.Text(
            [
                ('ok', str(
                    overview[1])), ('text', ' passed   '), ('error', str(
                overview[0])), ('text', ' failed   '), ('warning', str(
                overview[2])), ('text', ' warning   '), ('info', str(
                overview[3])), ('text', ' ommited')])
        footer = urwid.AttrMap(
            TextButton(
                '< Back to main menu',
                align='left',
                on_press=self.choose_test),
            'button')

        results_button = LineButton([('text', 'View detailed results')])
        email_button = LineButton([('text', 'Email')])

        urwid.connect_signal(
            results_button,
            'click',
            lambda _: self.display_test_result(result, title, urn))
        urwid.connect_signal(
            email_button, 'click', lambda _: self.email_prompt(result, title, urn))

        card = Card(urwid.Pile([header, DIV, subtitle, DIV, overview, DIV,
                                results_button, email_button]), footer=footer)
        self.app.render(card)

    def display_test_result(self, result, title, urn):
        display_test = DisplayTest(result)
        footer = self.get_footer('< Back to result overview',
                                 lambda _: self.display_overview(result, title, urn))
        card = Card(display_test, footer=footer)
        self.app.render(card)

    def email_prompt(self, result, title, urn):
        header = urwid.Text(('header red', 'Email result'))
        subtitle = urwid.Text(
            ('text', 'The quick brown fox jumps over the lazy dog'))
        content = urwid.Pile([header, DIV, subtitle])
        card = FormCard(
            content,
            ['Email'],
            'Send',
            lambda form, email: self.send_email(email.strip(), result, title, urn) if validate_email(
                email) else form.set_error("Invalid email"),
            lambda _: self.display_overview(result, title, urn))

        self.app.render(card)

    def send_email(self, email, result, title, urn):
        email_result = map(lambda r: {"name": r["name"], "value": r["result"], "data": r["extra_data"]}, result)
        response = send_result(email, email_result, title, urn)
        header = urwid.Text(('header red', title))
        subtitle = urwid.Text(
            ('text', response))

        content = urwid.Pile([header, DIV, subtitle])
        footer = self.get_footer('< Back to result overview',
                                 lambda _: self.display_overview(result, title, urn))
        card = Card(content, footer=footer)

        self.app.render(card)

    def get_footer(self, text, cb):
        return urwid.AttrMap(
            TextButton(
                text,
                align='left',
                on_press=(cb)),
            'button')
