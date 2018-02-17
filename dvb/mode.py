class Mode:
    TRAM = 'Tram'
    CITY_BUS = 'CityBus'
    INTERCITY_BUS = 'IntercityBus'
    SUBURBAN_RAILWAY = 'SuburbanRailway'
    TRAIN = 'Train'
    CABLEWAY = 'Cableway'
    FERRY = 'Ferry'
    HAILED_SHARED_TAXI = 'HailedSharedTaxi'

    @staticmethod
    def all():
        return [Mode.TRAM, Mode.CITY_BUS, Mode.INTERCITY_BUS, Mode.SUBURBAN_RAILWAY, Mode.TRAIN, Mode.CABLEWAY,
                Mode.FERRY, Mode.HAILED_SHARED_TAXI]
