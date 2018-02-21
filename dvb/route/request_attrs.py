from dvb.mot_type import MotType


class MobilitySettings:
    class IndividualEntranceOptions:
        ANY = 'Any'  # Einstieghöhe beliebig
        SMALL = 'Small'  # Einstieg mit kleiner Stufe
        NO_STEP = 'NoStep'  # Einstieg ohne Stufe

    @staticmethod
    def no_restriction() -> dict:
        """ohne Einschränkungen"""
        return dict(mobilityRestriction='None')

    @staticmethod
    def high() -> dict:
        """Rollstuhlfahrer ohne Hilfe"""
        return dict(mobilityRestriction='High')

    @staticmethod
    def medium() -> dict:
        """Rollator, Kinderwagen"""
        return dict(mobilityRestriction='Medium')

    @staticmethod
    def individual() -> dict:
        return dict(
            mobilityRestriction='Individual',
            solidStairs=True,  # keine festen Treppen
            escalators=False,  # keine Rolltreppen
            leastChange=False,  # Möglichst wenig umsteigen
            entrance=MobilitySettings.IndividualEntranceOptions.ANY,  # Einstieghöhe -> IndividualEntranceOptions
        )


class StandardSettings:
    class MaxChanges:
        UNLIMITED = 'Unlimited'
        TWO = 'Two'
        ONE = 'One'
        NONE = 'None'  # nur Direktverbindungen

    class WalkingSpeed:
        VERY_SLOW = 'VerySlow'
        SLOW = 'Slow'
        NORMAL = 'Normal'
        FAST = 'Fast'
        VERY_FAST = 'VeryFast'

    class FootpathDistanceToStop:
        FIVE = 5
        TEN = 10
        FIFTEEN = 15
        TWENTY = 20
        THIRTY = 30

    def __init__(self):
        self._dict = dict(
            maxChanges=StandardSettings.MaxChanges.UNLIMITED,
            walkingSpeed=StandardSettings.WalkingSpeed.NORMAL,
            footpathToStop=StandardSettings.FootpathDistanceToStop.FIVE,
            mot=MotType.all_request(),
            includeAlternativeStops=True,  # Nahegelegene Alternativhaltestellen einschließen
        )

    @property
    def max_changes(self) -> MaxChanges:
        return self._dict['maxChanges']

    @max_changes.setter
    def max_changes(self, value: MaxChanges):
        self._dict['maxChanges'] = value

    @property
    def walking_speed(self) -> WalkingSpeed:
        return self._dict['walkingSpeed']

    @walking_speed.setter
    def walking_speed(self, value: WalkingSpeed):
        self._dict['walkingSpeed'] = value

    @property
    def footpath_to_stop(self) -> FootpathDistanceToStop:
        return self._dict['footpathToStop']

    @footpath_to_stop.setter
    def footpath_to_stop(self, value: FootpathDistanceToStop):
        self._dict['footpathToStop'] = value

    @property
    def mot(self) -> MotType:
        return self._dict['mot']

    @mot.setter
    def mot(self, value: MotType):
        self._dict['mot'] = value

    @property
    def include_alternative_stops(self) -> bool:
        return self._dict['includeAlternativeStops']

    @include_alternative_stops.setter
    def include_alternative_stops(self, value: bool):
        self._dict['includeAlternativeStops'] = value
