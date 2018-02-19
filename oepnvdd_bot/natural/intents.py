import json
import logging
import os

import requests


def catch_key_index(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except KeyError or IndexError as e:
            logging.info(f'Key/Index Error on {e}')
            return None

    return wrapped


class Intent:
    class Type:
        DEPARTURE = 'departure'
        ROUTE = 'route'
        DISRUPTIONS = 'disruptions'
        LOCATION_SEARCH = 'location_search'

    def __init__(self, entities: dict):
        self.entities = entities

    def __repr__(self):
        return f'{self.type.upper()} Intent'

    @property
    @catch_key_index
    def type(self) -> Type:
        return self.entities['intent'][0]['value']

    @property
    @catch_key_index
    def locations(self) -> [str]:
        locations = [loc['value'] for loc in self.entities['location']]
        return locations

    @property
    @catch_key_index
    def origin(self) -> str:
        return self.entities['origin'][0]['value']

    @property
    @catch_key_index
    def destination(self) -> str:
        return self.entities['destination'][0]['value']

    @property
    @catch_key_index
    def lines(self) -> [str]:
        lines = [line['value'] for line in self.entities['line_identifier']]
        return lines


def parse_intent(message: str) -> Intent or None:
    response = requests.get(
        url='https://api.wit.ai/message',
        params=dict(v='20180218', q=message),
        headers=dict(Authorization='Bearer {}'.format(os.getenv('WITAI_SERVER_ACCESS_TOKEN'))),
    )
    if response.status_code != 200:
        logging.error(f'wit.ai error {response.status_code} {response.text}')
        return None
    params = json.loads(response.text)

    try:
        _ = params['entities']['intent'][0]  # validate that wit.ai actually found an intent
        return Intent(params['entities'])
    except KeyError:
        return None
