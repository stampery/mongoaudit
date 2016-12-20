# -*- coding: utf-8 -*-

import urwid
from testers import *


div = urwid.Divider()
hr = urwid.AttrMap(urwid.Divider('_'), 'hr')


def pad(w, left=2, right=2):
    return urwid.Padding(w, left=left, right=right)


class TextButton(urwid.Button):
    """
    Args:
      label (str): label for the text button
      on_press (function): callback
      user_data(): user_data for on_press
      align (str): (default right)
    """

    def __init__(self, label, on_press=None, user_data=None, align='right'):
        super(TextButton, self).__init__(
            label, on_press=on_press, user_data=user_data)
        self._label.align = align
        cols = urwid.Columns([self._label])
        super(urwid.Button, self).__init__(cols)


class Card(urwid.WidgetWrap):
    """
    Args:
      content (urwid.Widget):
      header (urwid.Widget):
      footer (urwid.Widget):
    """

    def __init__(self, content, header=None, footer=None):
        wlist = []
        if header:
            wlist.append(header)
        wlist.extend([div, pad(content)])
        if footer:
            wlist.extend([hr, div, pad(footer)])
        wlist.append(div)
        card = urwid.AttrMap(urwid.Pile(wlist), 'card')
        urwid.WidgetWrap.__init__(self, card)


class ObjectButton(urwid.Button):

    def __init__(self, content, on_press=None, user_data=None):
        self.__super.__init__('', on_press=on_press, user_data=user_data)

        super(urwid.Button, self).__init__(content)


class LineButton(ObjectButton):
    """
    Creates a LineBox button with an image on the left column and text on the right
    Args:
      text ((palette_class, str)[]): array of string tuples
    """

    def __init__(self, text):
        content = urwid.Pile([urwid.SelectableIcon(
            s, 0) if i == 0 else urwid.Text(s) for i, s in enumerate(text)])
        lbox = urwid.LineBox(urwid.Pile([urwid.Padding(
            content, left=3, right=3)]))
        self.__super.__init__(urwid.AttrMap(urwid.Pile(
            [lbox]), 'image button', 'image button focus'))


class ImageButton(ObjectButton):
    """
    Creates a LineBox button with an image on the left column and text on the right
    Args:
      pic (urwid.Pile): object created with picRead
      text ((palette_class, str)[]): array of string tuples
    """

    def __init__(self, pic, text):
        content = urwid.Pile([urwid.SelectableIcon(
            s, 0) if i == 0 else urwid.Text(s) for i, s in enumerate(text)])
        lbox = urwid.LineBox(urwid.Pile([div, urwid.Padding(
            urwid.Columns([(8, pic), content], 4), left=3, right=3), div]))
        self.__super.__init__(urwid.AttrMap(urwid.Pile(
            [lbox]), 'image button', 'image button focus'))


class InputField(urwid.WidgetWrap):
    """
    Creates an input field with underline and a label
    Args:
      label (str): label for the input
      label_width (int): label width (default 15 characters)
    """

    def __init__(self, label="", label_width=15, next=False):
        self.label, self.next = label, next
        self.edit = urwid.Padding(urwid.Edit(), left=1, right=1)
        label = urwid.LineBox(urwid.Text(label), tlcorner=' ', tline=' ', lline=' ',
                              trcorner=' ', blcorner=' ', rline=' ', brcorner=' ', bline=' ')
        lbox = urwid.AttrMap(urwid.LineBox(self.edit, tlcorner=' ', tline=' ', lline=' ',
                                           trcorner=' ', blcorner=' ', rline=' ', brcorner=' '), 'input', 'input focus')
        cols = urwid.Columns([(label_width, label), lbox])
        urwid.WidgetWrap.__init__(self, cols)

    def get_text(self):
        """
        Returns:
          str: value of the input field
        """
        return self.edit.original_widget.get_text()[0]

    def get_label(self):
        """
        Returns:
          str: label for the input field
        """
        return self.label

    def keypress(self, size, key):
        if key is 'enter' and self.next:
            self.next()
        else:
            return self.__super.keypress(size, key)


class FormCard(urwid.WidgetWrap):
    """
    Args:
      content (urwid.Widget): any widget that can be piled
      field_labels (str[]): labels for the input_fields
      btn_label (str): label for the button
      cb (function): callback to invoke when the form button is pressed
      back (function): card to render when going back
    Note:
      cb must take the same amount of arguments as labels were passed and each parameter
      in the callback must be named as the label but in snake case and lower case e.g.
      'Field Name' =>  field_name
    """

    def __init__(self, content, field_labels, btn_label, cb, back=None):
        self.fields, self.cb = [], cb
        for label in field_labels:
            self.fields.append(InputField(label, next=self.next))
        input_fields = urwid.Pile(self.fields)
        self.error_field = urwid.Text('')
        error_row = urwid.Columns([(17, urwid.Text('')), self.error_field])
        buttons = [TextButton(btn_label, on_press=self.next)]
        if back:
            buttons.insert(0, TextButton('Back', align='left', on_press=back))
        footer = urwid.AttrMap(urwid.Columns(buttons), 'button')

        card = Card(urwid.Pile(
            [content, input_fields, error_row]), footer=footer)
        urwid.WidgetWrap.__init__(self, card)

    def next(self, _button=None):
        self.cb(form=self, **(self.get_field_values()))

    def get_field_values(self):
        """
        Returns:
          dict: the keys are the labels of the fields in snake_case
        """
        values = dict()
        for field in self.fields:
            values[field.get_label().lower().replace(" ", "_")
                   ] = field.get_text()

        return values

    def set_error(self, msg):
        """
        Args:
          msg (str): error message
        """
        self.error_field.set_text(('error', msg))


class TestRunner(urwid.WidgetWrap):
    """
    Run the test while displaying the progress

    Args:
      title (str): title to pass to the callback
      cred (dict(str: str)): credentials
      tests (Test[]): tests to run
      app (App):
      cb (function):  callback to call when the tests finish running
    """

    def __init__(self, title, cred, tests, app, cb):
        self.title = title
        self.cb = cb
        self.number_of_test = len(tests)
        self.app = app

        self.tester = Tester(cred, tests)

        self.progress_text = urwid.Text(
            ('progress', '0/' + str(self.number_of_test)))
        running_display = urwid.Columns(
            [(14, urwid.Text(('text', 'Running check'))), self.progress_text])
        self.progress_bar = CustomProgressBar(
            'progress', 'remaining', 0, self.number_of_test)
        self.text_running = urwid.Text(('text', ''))
        box = urwid.BoxAdapter(urwid.Filler(
            self.text_running, valign='top'), 3)
        pile = urwid.Pile([div, running_display, self.progress_bar, div, box])
        urwid.WidgetWrap.__init__(self, pile)

    def each(self, test):
        """
        Update the description of the test currently running
        """
        current = self.progress_bar.get_current() + 1
        self.progress_text.set_text(
            ('progress', str(current) + '/' + str(self.number_of_test)))
        self.progress_bar.set_completion(current)
        self.text_running.set_text('Checking if ' + test.title + '...')
        self.app.loop.draw_screen()

    def run(self):
        """
        run tests
        """
        self.tester.run(self.each, self.end)

    def end(self, res):

        self.cb(res)


class CustomProgressBar(urwid.ProgressBar):
    """
    ProgressBar that displays a semigraph instead of a percentage
    """
    semi = u'▁▂▃▄▅▆▇█'

    def get_text(self):
        """
        Return the progress bar percentage.
        """
        return min(100, max(0, int(self.current * 100 / self.done)))

    def get_current(self):
        """
        Return the current value of the ProgressBar
        """
        return self.current

    def get_done(self):
        """
        Return the end value of the ProgressBar
        """
        return self.done

    def render(self, size, focus=False):
        """
        Render the progress bar.
        """
        (maxcol,) = size
        cf = float(self.current) * maxcol / self.done
        ccol = int(cf)
        txt = urwid.Text([(self.normal, self.semi[1] * ccol),
                          (self.complete, self.semi[1] * (maxcol - ccol))])
        c = txt.render(size)

        return c
