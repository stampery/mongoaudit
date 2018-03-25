# -*- coding: utf-8 -*-
import urwid
import math

from .picmagic import read as picRead
from .testers.testers import Tester
from .tools import validate_uri, send_result, load_test, validate_email
from .widgets import TestRunner, Card, TextButton, ImageButton, \
    DIV, FormCard, LineButton, DisplayTest
from functools import reduce


class Cards(object):
    def __init__(self, app):
        self.app = app
        self.tests = load_test('tests.json')

    def welcome(self):
        pic = picRead('welcome.bmp', align='right')

        text = urwid.Text([
            ('text bold', self.app.name),
            ('text', ' is a CLI tool for auditing MongoDB servers, detecting poor security '
                     'settings and performing automated penetration testing.\n\n'),
            ('text italic', "\"With great power comes great responsibility\". Unauthorized "
                            "access to strangers' computer systems is a crime "
                            "in many countries. Take care.")
        ])
        button = urwid.AttrMap(
            TextButton(
                "Ok, I'll be careful!", on_press=self.choose_test), 'button')

        card = Card(text, header=pic, footer=button)
        self.app.render(card)

    def choose_test(self, *_):
        txt = urwid.Text(
            [('text bold',
              self.app.name),
             ' provides two distinct test suites covering security in different '
             'depth. Please choose which one you want to run:'])

        basic = ImageButton(
            picRead('bars_min.bmp'),
            [('text bold', 'Basic'),
             ('text', 'Analyze server perimeter security. (Does not require '
                      'valid authentication credentials, just the URI)')])
        advanced = ImageButton(
            picRead('bars_max.bmp'),
            [('text bold', 'Advanced'),

             ('text', 'Authenticate to a MongoDB server and analyze security '
                      'from inside. (Requires valid credentials)')])

        content = urwid.Pile([txt, DIV, basic, advanced])

        basic_args = {
            'title': 'Basic',
            'label': 'This test suite will only check if your server implements all the '
                     'basic perimeter security measures advisable for production databases. '
                     'For a more thorough analysis, please run the advanced test suite.\n\n'
                     'Please enter the URI of your MongoDB server',
            'uri_example': 'domain.tld:port',
            'tests': self.tests['basic']}
        urwid.connect_signal(
            basic, 'click', lambda _: self.uri_prompt(**basic_args))
        advanced_args = {
            'title': 'Advanced',
            'label': 'This test suite authenticates to your server using valid credentials '
                     'and analyzes the security of your deployment from inside.\n\n'
                     'We recommend to use the same credentials as you use for your app.\n'
                     'Please enter your MongoDB URI in this format:',
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
            urwid.Text(('text bold', title + ' test suite')),
            DIV,
            urwid.Text([label + ' (', ('text italic', uri_example), ')'])
        ])

        def _next(form, uri):
            form.set_message("validating URI")
            cred = validate_uri(uri)
            if cred:
                form.set_message("Checking MongoDB connection...")
                tester = Tester(cred, tests)
                if tester.info:
                    self.run_test(cred, title, tester, tests)
                else:
                    form.set_message("Couldn't find a MongoDB server", True)
            else:
                form.set_message("Invalid domain", True)


        form = FormCard(
            {"content": intro, "app": self.app}, ['URI'],
            'Run ' + title.lower() + ' test suite',
            {'next': _next, 'back': self.choose_test})
        self.app.render(form)

    def run_test(self, cred, title, tester, tests):
        """
        Args:
          cred (dict(str: str)): credentials
          title (str): title for the TestRunner
          tests (Test[]): test to run
        """
        test_runner = TestRunner(title, cred, tests,
                                 {"tester":tester, "callback": self.display_overview})
        # the name of the bmp is composed with the title
        pic = picRead('check_' + title.lower() + '.bmp', align='right')

        footer = self.get_footer('Cancel', self.choose_test)
        card = Card(test_runner, header=pic, footer=footer)
        self.app.render(card)
        test_runner.run(self.app)

    def display_overview(self, result, title, urn):
        """
        Args:
            result (dict()): the result returned by test_runner
        """

        def reduce_result(res, values):
            return reduce_result(res % values[-1], values[:-1]) + [res / values[-1]] \
                if bool(values) else []

        # range 4 because the possible values for result  are [False, True,
        # 'custom', 'omitted']
        values = [(len(result) + 1) ** x for x in range(4)]

        total = reduce(lambda x, y: x + values[y['result']], result, 0)
        header = urwid.Text(('text bold', 'Results overview'))
        subtitle = urwid.Text(
            ('text', 'Finished running ' + str(len(result)) + " tests:"))
        overview = reduce_result(total, values)
        overview = urwid.Text([
            ('passed', str(int(math.floor(overview[1])))), ('text', ' passed   '),
            ('failed', str(int(math.floor(overview[0])))), ('text', ' failed   '),
            ('warning', str(int(math.floor(overview[2])))), ('text', ' warning   '),
            ('info', str(int(math.floor(overview[3])))), ('text', ' omitted')])
        footer = urwid.AttrMap(
            TextButton(
                '< Back to main menu',
                align='left',
                on_press=self.choose_test),
            'button')

        results_button = LineButton([('text', '> View brief results summary')])
        email_button = LineButton([('text', '> Email me the detailed results report')])

        urwid.connect_signal(
            results_button,
            'click',
            lambda _: self.display_test_result(result, title, urn))
        urwid.connect_signal(
            email_button, 'click', lambda _: self.email_prompt(result, title, urn))

        card = Card(urwid.Pile([header, subtitle, overview, DIV,
                                results_button, email_button]), footer=footer)
        self.app.render(card)

    def display_test_result(self, result, title, urn):
        display_test = DisplayTest(result)
        footer = self.get_footer('< Back to results overview',
                                 lambda _: self.display_overview(result, title, urn))
        card = Card(display_test, footer=footer)
        self.app.render(card)

    def email_prompt(self, result, title, urn):
        header = urwid.Text(('text bold', 'Send detailed results report via email'))
        subtitle = urwid.Text([
            ('text', 'The email report contains detailed results of each of the runned tests, '
                     'as well as links to guides on how to fix the found issues.\n\n'),
            ('text italic', 'You will be included into a MongoDB critical security bugs '
                            'newsletter. We will never SPAM you, we promise!')
        ])
        content = urwid.Pile([header, DIV, subtitle])
        card = FormCard(
            {"content": content, "app": self.app},
            ['Email'],
            'Send report',
            {
                'next': lambda form, email: self.send_email(email.strip(), result, title, urn) \
                if validate_email(email) else form.set_message("Invalid email address", True),
                'back': lambda _: self.display_overview(result, title, urn)
            })


        self.app.render(card)

    def send_email(self, email, result, title, urn):
        email_result = [{"name": val["name"], "value": val["result"],
                         "data": val["extra_data"]} for val in result]
        response = send_result(email, email_result, title, urn)
        header = urwid.Text(('text bold', 'Send detailed results report via email'))
        subtitle = urwid.Text(
            ('text', response))

        content = urwid.Pile([header, DIV, subtitle])
        footer = self.get_footer('< Back to results overview',
                                 lambda _: self.display_overview(result, title, urn))
        card = Card(content, footer=footer)

        self.app.render(card)

    @staticmethod
    def get_footer(text, callback):
        return urwid.AttrMap(
            TextButton(
                text,
                align='left',
                on_press=(callback)),
            'button')
