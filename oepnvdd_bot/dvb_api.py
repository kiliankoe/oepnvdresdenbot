import logging
from datetime import datetime

from dvb import Departure, Stop, Route

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

    departure_res = Departure.for_stop_id(stop_id, time=time)
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


def format_route(route: Route) -> str:
    # 13:58 bis 14:23 ~ 25 Min. 1 Umstieg
    # 13:58 Albertplatz
    #       6 Niedersedlitz
    # 14:13 Blasewitz Schillerplatz
    #       3 Min. Umsteigezeit
    # 14:16 Blasewitz Schillerplatz
    #       65 Luga
    # 14:23 Altenberger Platz
    first_stop = route.partial_routes[0].regular_stops[0]
    last_stop = route.partial_routes[-1].regular_stops[-1]
    route_str = '{} bis {} ~ {} Min. {} Umstieg(e)'.format(first_stop.departure_time.strftime('%H:%M'),
                                                         last_stop.arrival_time.strftime('%H:%M'),
                                                         route.duration, route.interchanges)
    for pr in route.partial_routes:
        if len(pr.regular_stops) > 0:
            departure = pr.regular_stops[0]
        else:
            continue
        # arrival = pr.regular_stops[-1]
        mot = pr.mot.name
        direction = pr.mot.direction if pr.mot.direction is not None else ''
        route_str += '\n{} {}'.format(departure.departure_time.strftime('%H:%M'), departure.name.strip())
        route_str += '\n      {} {}'.format(mot, direction)

    return route_str
