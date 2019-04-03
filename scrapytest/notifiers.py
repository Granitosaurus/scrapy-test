import json
from urllib.request import Request, urlopen


def post_json(url, json_data):
    json_data = json_data.encode('utf-8')
    req = Request(url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Content-Length', len(json_data))
    return urlopen(req, json_data)


class SlackNotifier:
    """
    Notifier for slack messaging service that uses "incoming webhooks" app:
    https://slack.com/apps/A0F7XDUAZ-incoming-webhooks
    """
    def __init__(self, url, channel, username='', icon_emoji='', maintainer=''):
        """
        :param url: incoming webhooks url
        :param channel: #channel or @user where message will be sent to
        :param username: bot's displayed name
        :param icon_emoji: bot's displayed avatar e.g. :cat:
        :param maintainer: maintainer's username who will be mentioned on exit code 1 e.g. @here or @bernard
        """
        self.url = url
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji
        self.maintainer = maintainer

    @classmethod
    def from_config(cls, config):
        return cls(
            url=config['slack_url'],
            channel=config['slack_channel'],
            username=config.get('slack_username', ''),
            icon_emoji=config.get('slack_icon_emoji', ''),
            maintainer=config.get('slack_maintainer', ''),
        )

    def notify(self, code, msg, context=None):
        """Send notification based on code, context will be included in message header"""
        msg = f"Finished tests for \"{context or ''}\" {self.maintainer if code == 1 else ''}\n```{msg}```"
        data = {
            'channel': self.channel,
            'username': self.username,
            'icon_emoji': self.icon_emoji,
            'text': msg,
            'link_names': '1',
        }
        # click.echo(f'sending msg to slack: {data["channel"]}')
        resp = post_json(self.url, json.dumps(data))
        assert resp.code == 200
        assert resp.read() == b'ok'
        return resp
