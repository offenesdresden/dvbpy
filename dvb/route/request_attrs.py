from dvb.mot_type import MotType


class MobilitySettings:
    class IndividualEntranceOptions:
        ANY = 'Any'  # Einstieghöhe beliebig
        SMALL = 'Small'  # Einstieg mit kleiner Stufe
        NO_STEP = 'NoStep'  # Einstieg ohne Stufe

    NO_RESTRICTION = dict(mobilityRestriction='None')  # ohne Einschränkungen
    HIGH = dict(mobilityRestriction='High')  # Rollstuhlfahrer ohne Hilfe
    MEDIUM = dict(mobilityRestriction='Medium')  # Rollator, Kinderwagen
    INDIVIDUAL = dict(
        mobilityRestriction='Individual',
        solidStairs=True,  # keine festen Treppen
        escalators=False,  # keine Rolltreppen
        leastChange=False,  # Möglichst wenig umsteigen
        entrance=IndividualEntranceOptions.ANY,  # Einstieghöhe -> IndividualEntranceOptions
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
    def max_changes(self):
        return

    @max_changes.setter
    def max_changes(self, value):
        pass
