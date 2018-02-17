from datetime import datetime

from .util.date import sap_date_to_datetime
from .mode import Mode
from .network import post


class Departure:
    class State:
        IN_TIME = 'InTime'
        DELAYED = 'Delayed'
        # CANCELLED = '?'

    def __init__(self, _dict):
        self._dict = _dict

    def __repr__(self):
        return '{} {} in {}'.format(self.line_name, self.direction, self.fancy_eta())

    @staticmethod
    def for_stop(stop_id: int, time: datetime = None, is_arrival: bool = None, limit: int = None,
                 transport_modes: [Mode] = None) -> dict:
        """Fetch a list of departures for a given stop_id"""

        time = datetime.now() if time is None else time
        is_arrival = False if is_arrival is None else is_arrival
        limit = 0 if limit is None else limit
        transport_modes = Mode.all() if transport_modes is None else transport_modes

        res = post('https://webapi.vvo-online.de/dm', {
            'stopid': stop_id,
            'time': time.isoformat(),
            'isarrival': is_arrival,
            'limit': limit,
            'mot': transport_modes
        })

        out = dict()
        out['departures'] = [Departure(dep) for dep in res.get('Departures')]
        out['expiration_time'] = sap_date_to_datetime(res.get('ExpirationTime'))
        out['name'] = res.get('Name')
        out['place'] = res.get('Place')
        return out

    @property
    def id(self) -> str or None:
        return self._dict.get('Id')

    @property
    def line_name(self) -> str or None:
        return self._dict.get('LineName')

    @property
    def direction(self) -> str or None:
        return self._dict.get('Direction')

    @property
    def mode(self) -> Mode or None:
        return self._dict.get('Mot')

    @property
    def state(self) -> State or None:
        return self._dict.get('State')

    @property
    def scheduled_time(self) -> datetime or None:
        """Scheduled time of arrival"""
        scheduled_time = self._dict.get('ScheduledTime')
        return sap_date_to_datetime(scheduled_time)

    @property
    def real_time(self) -> datetime or None:
        """Actual time of arrival"""
        real_time = self._dict.get('RealTime')
        return sap_date_to_datetime(real_time)

    @property
    def platform(self) -> dict or None:
        return self._dict.get('Platform')

    @property
    def route_changes(self) -> [str] or None:
        return self._dict.get('RouteChanges')

    @property
    def diva(self) -> dict or None:
        return self._dict.get('Diva')

    def eta(self, from_date: datetime = None) -> int:
        """Estimated time of arrival in minutes from now. Returns scheduled ETA if real time is unknown."""
        from_date = datetime.now() if from_date is None else from_date

        if self.real_time is None:
            return self.scheduled_eta()
        diff = self.real_time - from_date
        return int(diff.seconds / 60)

    def scheduled_eta(self, from_date: datetime = None) -> int:
        """Estimated time of arrival in minutes from now as scheduled, disregarding any known real time ETA."""
        from_date = datetime.now() if from_date is None else from_date

        diff = self.scheduled_time - from_date
        return int(diff.seconds / 60)

    def fancy_eta(self, from_date: datetime = None) -> str:
        """Estimated time of arrival as string with offset if real time information is available."""
        from_date = datetime.now() if from_date is None else from_date

        if self.real_time is None:
            return str(self.scheduled_eta(from_date=from_date))

        time_diff = self.real_time - self.scheduled_time
        minute_diff = int(time_diff.seconds / 60)

        scheduled_eta = self.scheduled_eta(from_date=from_date)

        if from_date > self.scheduled_time:
            scheduled_eta = -(24 * 60 - scheduled_eta)

        if scheduled_eta >= 60:
            hours = int(scheduled_eta / 60)
            minutes = scheduled_eta % 60
            scheduled_eta_str = '{}:{:02}'.format(hours, minutes)
        else:
            scheduled_eta_str = str(scheduled_eta)

        if minute_diff == 0:
            return scheduled_eta_str
        else:
            diff_str = str(minute_diff) if minute_diff < 0 else '+' + str(minute_diff)
            return scheduled_eta_str + diff_str
