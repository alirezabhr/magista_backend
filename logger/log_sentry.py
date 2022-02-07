import json

from sentry_sdk import capture_message


def sentry_data_json(location, response, request=None):
    return json.dumps({'location': location, 'response': response, 'request': request})


def log_message_sentry(location, response, request, level='warning'):
    capture_message(sentry_data_json(location, response, request), level=level)

