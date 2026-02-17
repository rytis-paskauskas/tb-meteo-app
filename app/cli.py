import argparse
import logging
from datetime import datetime
import pandas as pd

from pandas.core.generic import ExponentialMovingWindow
from .config import configure, load_config
from .identifiers import VALID_IDENTIFIERS
#from .tb_client import fetch_data
from .exporter import export_csv
from tb_rest_client.rest_client_ce import RestClientCE, EntityId
from tb_rest_client.rest import ApiException
from meteoresampler import ts_to_pandas, resample, cyclicdiff1d, DataSpec

def _parse_datetime(value: str) -> datetime:
    """
    Parse datetime from ISO-like string.
    Raises argparse.ArgumentTypeError if invalid.
    """
    try:
        # Accept ISO 8601 strings
        return datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime format: '{value}'. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)."
        )


def main():
    parser = argparse.ArgumentParser(prog="tb-meteo-app")

    parser.add_argument(
        "identifier",
        nargs="?",
        help=f"One of: {', '.join(VALID_IDENTIFIERS.keys())}",
    )

    parser.add_argument("--start", help="Start date (ISO format)")
    parser.add_argument("--end", help="End date (ISO format)")
    parser.add_argument("--out", help="Output CSV filename")
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Configure API endpoint and credentials",
    )

    args = parser.parse_args()

    if args.configure:
        configure()
        return

    if not args.identifier:
        parser.error("Identifier required unless using --configure")

    if args.identifier not in VALID_IDENTIFIERS:
        parser.error(
            f"Invalid identifier. Choose from: {', '.join(VALID_IDENTIFIERS.keys())}"
        )

    if not args.start or not args.end:
        parser.error("Both --start and --end must be provided.")

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    # Parse datetimes
    beg_dt = _parse_datetime(args.start)
    end_dt = _parse_datetime(args.end)
    print(f"start={beg_dt}")
    print(f"end={end_dt}")
    days = (end_dt - beg_dt).days
    print(f"days={days}")
    
    if beg_dt >= end_dt:
        parser.error("--start must be earlier than --end.")
        
    config = load_config()

    beg_ts = pd.Timestamp(beg_dt).tz_localize(config['timezone']).tz_convert("UTC").timestamp()
    end_ts = pd.Timestamp(end_dt).tz_localize(config['timezone']).tz_convert("UTC").timestamp()

    item = VALID_IDENTIFIERS[args.identifier]
    entity = EntityId(item['device_id'], item['device_type'])
    tb_opts = {'limit': (1+days)*144, 'order_by': 'ASC', 'use_strict_data_types': True}
    try: 
        with RestClientCE(base_url=config['endpoint']) as rest_client:
            rest_client.login(username=config['username'], password=config['password'])
            series = rest_client.get_timeseries(entity, ",".join(item['telemetry_keys']), int(1000*beg_ts), int(1000*end_ts), **tb_opts)

        if series is None or len(series)==0:
            raise ValueError("This query returned an empty series")
        df = ts_to_pandas(series)
        df.index = pd.to_datetime(df.index, unit='ms')
 
        rng = pd.DataFrame(
            index=(
                pd.date_range(
                    start=args.start,
                    end=args.end,
                    freq=item['resampling_frequency'],
                    tz=config['timezone']
                )
                .tz_convert("UTC")
                .tz_localize(None)
                .astype("datetime64[s]")
            )
        )

        fast = DataSpec(df,item['telemetry_sampling'])
        slow = DataSpec(rng, item['resampling_frequency'])
        gapt = item['triggers_gap']
        result = resample(fast, gapt, slow, item['resampling_specs'])

        # Sometimes result comes out as 'object' check: result[0].info()
        for t in result:
            for s in t.columns:
                t[s] = t[s].astype('float')
            
        if args.identifier == 'meteohelix':
            # Change pressure units from Pa to mbar (hPa)
            result = pd.concat(result)
            k = [t['result_key'] for t in item['resampling_specs'] if t['key'] == 'p']
            if k is None or len(k) == 0:
                raise ValueError('Could not identify pressure telemetry')
            result[k] *= 0.01
        elif args.identifier == 'meteowind':
            # Change wind speed units from m/s to knots
            # Round direction to nearest integer degree
            result = pd.concat(result)
            k = [t['result_key'] for t in item['resampling_specs'] if t['key'] in ['ws', 'wsx']]
            if k is None or len(k) == 0:
                raise ValueError('Could not identify wind speed telemetry')
            result[k] *= 1.94384
            k = [t['result_key'] for t in item['resampling_specs'] if t['key'] in ['wd', 'wdx']]
            if k is None or len(k) == 0:
                raise ValueError('Could not identify wind direction telemetry')
            result[k] = result[k].round().astype('Int64')
        elif args.identifier == 'meteorain':
            k = [t['result_key'] for t in item['resampling_specs'] if t['key'] in ['rc', 'rcc']]
            period = dict({})
            for t in item['resampling_specs']:
                if t['key'] == 'rc':
                    period[t['result_key']] = 4096
                elif t['key'] == 'rcc':
                    period[t['result_key']] = 40.96
            _tmp = [cyclicdiff1d(t[k], period=period) for t in result]
            r_mm = [0.01*(t['rc'] + t['rcc']) for t in _tmp]
            for t in r_mm:
                t.name = 'rainfall'
            breakpoint()
            # 10 minute to 1 hour sampling
            # resamp = [t.resample(item['resampling_frequency'],label='right', closed='right').sum(min_count=6) for t in r_mm]
            # result = pd.concat(resamp).dropna()
            result = pd.concat(r_mm).dropna()

            result.index = result.index.tz_localize('UTC').tz_convert(config['timezone'])
            export_csv(result, args.out)

        breakpoint()
    except ApiException as e:
        breakpoint()
        if e.status == 500:
            print(e.reason)
            print(f"Try requesting fewer data (current request = {days} days")
            logging.exception(e)
    except ValueError as e:
        logging.exception(e)
