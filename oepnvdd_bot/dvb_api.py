import logging
from datetime import datetime

from dvb import Departure, Stop

_stop_id_cache = dict()


def departures_for_stop_name(stop_name: str, time: datetime = None, line_filter: [str] = None) -> (str, [Departure]):
    time = datetime.now() if time is None else time
    line_filter = [] if line_filter is None else line_filter

    if stop_name in _stop_id_cache:
        logging.debug(f'Found {stop_name} in cache.')
        stop = _stop_id_cache[stop_name]
    else:
        logging.debug(f'{stop_name} not in cache. Fetching id.')
        stop_res = Stop.find(stop_name)
        if len(stop_res.get('stops')) == 0:
            return []
        stop = stop_res['stops'][0].id
        _stop_id_cache[stop_name] = stop

    return departures_for_stop_id(stop, time, line_filter)


def departures_for_stop_id(stop_id: int, time: datetime = None, line_filter: [str] = None) -> (str, [Departure]):
    time = datetime.now() if time is None else time
    line_filter = [] if line_filter is None else line_filter

    departure_res = Departure.for_stop(stop_id, time=time)
    if len(line_filter) != 0:
        departures = list(filter(lambda d: d.line_name == line_filter[0], departure_res['departures']))
    else:
        departures = departure_res['departures']
    return departure_res['name'], departures


def format_departure(dep: Departure) -> str:
    line = dep.line_name.ljust(4)
    direction = dep.direction.ljust(16)[:16]
    eta = dep.fancy_eta()

    return f'{line} {direction} {eta}'
