import json
from datetime import datetime

from .network import post
from .util import sap_date_to_datetime, convert_to_snake_case


class Departure:
    @staticmethod
    def from_json(j: dict):
        # FIXME: This is a hack, but it simplifies stuff for now
        dep = Departure()
        keys_to_hide = ['scheduled_time', 'real_time']
        for key, val in j.items():
            key = convert_to_snake_case(key)
            key = '_' + key if key in keys_to_hide else key
            dep.__dict__[key] = val

        # short sanity check
        assert ('line_name' in dep.__dict__)
        assert ('direction' in dep.__dict__)
        return dep

    @staticmethod
    def fetch(stop_id: int):
        """Fetch a list of departures for a given stop_id"""
        res = post('https://webapi.vvo-online.de/dm', {
            'stopid': stop_id
        })
        j = json.loads(res)
        departures = [Departure.from_json(dep) for dep in j['Departures']]
        return departures

    def __repr__(self):
        return f'{self.line_name} {self.direction}'

    def scheduled_time(self) -> datetime or None:
        """Scheduled time of arrival"""
        return sap_date_to_datetime(self._scheduled_time)

    def real_time(self) -> datetime or None:
        """Actual time of arrival"""
        return sap_date_to_datetime(self._real_time)

    def eta(self, from_date: datetime = None) -> int:
        """Estimated time of arrival in minutes from now. Returns scheduled ETA if real time is unknown."""
        from_date = datetime.now() if from_date is None else from_date

        if self.real_time() is None:
            return self.scheduled_eta()
        diff = self.real_time() - from_date
        return int(diff.seconds / 60)

    def scheduled_eta(self, from_date: datetime = None) -> int:
        """Estimated time of arrival in minutes from now as scheduled, disregarding any known real time ETA."""
        from_date = datetime.now() if from_date is None else from_date

        diff = self.scheduled_time() - from_date
        return int(diff.seconds / 60)

    def fancy_eta(self, from_date: datetime = None) -> str:
        """Estimated time of arrival as string with offset if real time information is available."""
        from_date = datetime.now() if from_date is None else from_date

        if self.real_time() is None:
            return str(self.scheduled_eta(from_date=from_date))

        time_diff = self.real_time() - self.scheduled_time()
        minute_diff = int(time_diff.seconds / 60)
        diff_str = str(minute_diff) if minute_diff < 0 else '+' + str(minute_diff)
        return str(self.scheduled_eta(from_date=from_date)) + diff_str
