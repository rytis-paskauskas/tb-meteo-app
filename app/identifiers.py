from meteoresampler import Akima1D, Slerp1D

VALID_IDENTIFIERS = {
    "meteohelix": {
        "device_type": "ASSET",
        "device_id": "8f03bfb0-bc5e-11ef-b9ae-fb562b128918",
        "telemetry_keys": ["t", "p", "h", "s"],
        "telemetry_sampling": "10min",
        "resampling_frequency": "10min",
        "triggers_gap": "1h",
        "resampling_specs": [
            {"key": "t", "method": Akima1D(method="akima"),
             "result_key": "temperature"},
            {"key": "h", "method": Akima1D(method="makima"),
             "result_key": "rel_humidity"},
            {"key": "p", "method": Akima1D(method="akima"),
             "result_key": "atm_pressure"},
            {"key": "s", "method": Akima1D(method="makima"),
             "result_key": "downwelling_solar"}
            ]
    },
    "meteowind": {
        "device_type": "ASSET",
        "device_id": "cb1c8c00-bb9d-11ef-b9ae-fb562b128918",
        "telemetry_keys": ["ws","wd","wsx","wdx"],
        "telemetry_sampling": "10min",
        "resampling_frequency": "10min",
        "triggers_gap": "1h",
        "resampling_specs": [
            {'key': 'ws', 'method': Akima1D(method='makima'),
             'result_key': 'wind_speed'},
            {'key': 'wd', 'method': Slerp1D(period=360.0, out_offset=0),
             'result_key': 'wind_direction'},
            {'key': 'wsx', 'method': Akima1D(method='makima'),
             'result_key': 'gust_speed'},
            {'key': 'wdx', 'method': Slerp1D(period=360.0, out_offset=0),
             'result_key': 'gust_direction'}
        ]
    },
    "meteorain": {
        "device_type": "ASSET",
        "device_id": "7db64660-bc5e-11ef-b9ae-fb562b128918",
        "telemetry_keys": ["rc", "rcc"],
        "telemetry_sampling": None,
        "resampling_frequency": "10min",
        "triggers_gap": "1h",
        "resampling_specs": [
            {"key": "rc", "method": Slerp1D(period=4096, out_offset=0),
             "result_key": "rc"},
            {"key": "rcc", "method": Slerp1D(period=40.96, out_offset=0),
             "result_key": "rcc"}]
    }
}
