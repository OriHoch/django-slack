import unittest

from django_slack import slack_message
from django_slack.api import backend


class SlackTestCase(unittest.TestCase):
    def setUp(self):
        backend.reset()

    def assertMessageCount(self, count):
        self.assertEqual(len(backend.messages), count)

    def assertMessage(self, url=None, **kwargs):
        """Assert there was only one message sent with a URL and data values."""
        self.assertMessageCount(1)
        message = backend.messages[0]

        # Optionally assert the URL.
        if url is not None:
            self.assertEqual(url, message['url'])

        # Assert each input value in data.
        for kwarg, value in kwargs.items():
            self.assertEqual(value, message['data'][kwarg])


class TestEscaping(SlackTestCase):
    def test_simple_message(self):
        slack_message('test.slack', {'text': 'test'})
        self.assertMessage(text='test')

    def test_escaped(self):
        """Simple test of the Django escaping to illustrate problem."""
        slack_message('test.slack', {'text': '< > & " \''})
        self.assertMessage(text='&lt; &gt; &amp; &quot; &#39;')

    def test_escape_tag(self):
        """Test using the escape tag, but not escaping anything."""
        slack_message('escape.slack', {'text': 'test'})
        self.assertMessage(text='test')

    def test_escape_chars(self):
        """
        Test the characters Slack wants escaped.

        See https://api.slack.com/docs/formatting#how_to_escape_characters
        """
        slack_message('escape.slack', {'text': '< > &'})
        self.assertMessage(text='&lt; &gt; &amp;')

    def test_not_escape_chars(self):
        """
        Test normal HTML escaped characters that Slack doesn't want escaped.
        """
        slack_message('escape.slack', {'text': '" \''})
        self.assertMessage(text='" \'')
