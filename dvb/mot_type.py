class MotType:
    # These are relevant for Departure.mot and filtering for requests, see .all_request() below
    TRAM = 'Tram'
    CITY_BUS = 'CityBus'
    INTERCITY_BUS = 'IntercityBus'
    SUBURBAN_RAILWAY = 'SuburbanRailway'
    TRAIN = 'Train'
    CABLEWAY = 'Cableway'
    FERRY = 'Ferry'
    HAILED_SHARED_TAXI = 'HailedSharedTaxi'

    # The following (and some from above) exist solely in Route.mot_chain, at least afaict
    FOOTPATH = 'Footpath'
    BUS = 'Bus'
    RAPID_TRANSIT = 'RapidTransit'

    @staticmethod
    def all_request():
        """A list of all modes of transport relevant for departure monitor requests"""
        return [MotType.TRAM, MotType.CITY_BUS, MotType.INTERCITY_BUS, MotType.SUBURBAN_RAILWAY, MotType.TRAIN,
                MotType.CABLEWAY, MotType.FERRY, MotType.HAILED_SHARED_TAXI]
