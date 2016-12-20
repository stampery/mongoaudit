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
        export_button = LineButton([('text', 'Export results to filesystem')])
        email_button = LineButton([('text', 'View detailed results')])

        urwid.connect_signal(
            results_button, 'click', lambda _: self.display_test_result(result))

        card = Card(urwid.Pile([header, div, subtitle, div, overview, div,
                                results_button, export_button, email_button]), footer=footer)
        self.app.render(card)

    def display_test_result(self, result):
        def test_display(test, options):
            div_option = (div, options('weight', 1))
            title = (urwid.Text(
                ('text bold', test['title'])), options('weight', 1))
            caption = (urwid.Text(
                ('text', test['caption'])), options('weight', 1))
            severity = (urwid.Text(
                ('text', 'Severity: ' + ['High', 'Medium', 'Low'][test['severity']])), options('weight', 1))
            result = (urwid.Text(
                [('text', 'Result: '), (['error', 'ok', 'warning', 'info'][test['result']],
                 ' ' + ['✘', '✔', '?', '*'][test['result']]),
                 ('text', [' failed', ' passed', ' warning', ' omitted'][test['result']])]),
                options('weight', 1))
            message = (urwid.Text(
                ('text', test['message'])), options('weight', 1))
            temp = (urwid.Text(str(test)), options('weight', 1))
            return [div_option, title, div_option, caption, div_option, severity, result, div_option, message]

        def get_top_text():
            return 'header red', 'Test ' + str(self.currently_displayed) + '/' + str(total)

        def get_top_row(current, options):
            next_btn = urwid.AttrMap(TextButton('>', on_press=(
                lambda _: update_view(self, 'next'))), 'button')
            prev_btn = urwid.AttrMap(TextButton('<', on_press=(
                lambda _: update_view(self, 'prev'))), 'button')
            top_row = []
            focus = None
            if(current > 1):
                top_row.append((prev_btn, options('weight', 0)))
            top_row.append((urwid.Padding(urwid.Text(get_top_text()),
                                          left=25), options('weight', 1)))
            if(current < len(result) - 1):
                top_row.append((next_btn, options('weight', 0.2)))
            return top_row

        def update_view(self, btn):
            if(btn is 'prev'):
                self.currently_displayed -= 1
            elif(btn is 'next'):
                self.currently_displayed += 1
            self.top_columns.contents = get_top_row(
                self.currently_displayed, self.top_columns.options)
            if(self.currently_displayed > 1):
                self.top_columns.focus_position = 2 if btn is 'next' and self.currently_displayed < len(
                    result) - 1 else 0
            else:
                self.top_columns.focus_position = 1

            self.test_result.contents = test_display(
                result[self.currently_displayed - 1], self.test_result.options)

        self.currently_displayed = 0
        total = len(result)
        self.top_columns = urwid.Columns([])
        self.test_result = urwid.Pile([])
        update_view(self, 'next')
        top = urwid.Padding(self.top_columns, left=3, right=3)
        footer = urwid.AttrMap(TextButton('< Back to result overview', align='left', on_press=(
            lambda _: self.display_overview(result))), 'button')
        card = Card(urwid.Pile([top, self.test_result]), footer=footer)
        self.app.render(card)

    def display_results(self, title, list_walker, total):
        """
        Args:
          title (str): title used when displaying the results
          list_walker (urwid.SimpleListWalker): content to display in a ListBox
          total (int) : number of test finished
        """
        intro = urwid.Text(('text bold', title + ' test results'))
        footer = urwid.AttrMap(TextButton(
            'Back', align='left', on_press=self.choose_test), 'button')
        lbox = urwid.BoxAdapter(urwid.ListBox(list_walker), height=12)
        pile = urwid.Pile([intro, div, lbox, div, total, div])
        card = Card(pile, footer=footer)
        self.app.render(card)
