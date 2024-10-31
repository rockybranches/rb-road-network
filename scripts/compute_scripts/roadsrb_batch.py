#!python3
import os
import subprocess
import csv
import argparse
from ast import literal_eval
from collections import OrderedDict
from dotenv import load_dotenv

load_dotenv()


class MissingColumnsError(NotImplementedError):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.message = 'Please provide a csv file containing the columns: (Site, Lat, Lon).'
        # f' Columns in the csv you specified: {args[0]}')


class NoCSVGivenError(FileNotFoundError):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.message = 'The CSV file you provided was not found.'
        if args:
            self.message += f' : {args[0]}'


class Roads2PopBatchProcessor:
    def __init__(self, **kwds):
        self.cmdpath = os.path.join(
            os.environ['RB_SRC'],
            'scripts/compute_scripts/compute_justpop_result.sh')
        self.output_path = kwds.get(
            'output_dir', os.path.join(os.environ['RB_SRC'], 'output'))
        self.inputd = OrderedDict()
        self.cols = ['site', 'lat', 'lon']
        self.mode = kwds.get('mode', 'batch')
        print('mode=', self.mode)
        if self.mode == 'batch':
            self.csv_fpath = kwds.get('csv_fpath', None)
            if not self.csv_fpath:
                raise MissingColumnsError(())
            if not os.path.exists(self.csv_fpath):
                raise NoCSVGivenError(self.csv_fpath)
            self._read_csv()
        elif self.mode == 'serial':
            self.site, self.lat, self.lon =\
                Roads2PopBatchProcessor._parse_str_params(kwds['str_params'])

    @staticmethod
    def _format_site_str(sname):
        return ''.join(
            [l for l in sname if l not in [' ', '/', "'", '"', ':']])

    @staticmethod
    def _parse_str_params(str_params):
        site, lat, lon = tuple(literal_eval(str_params))
        site = Roads2PopBatchProcessor._format_site_str(site)
        return site, str(lat), str(lon)

    def _read_csv(self):
        print(f'reading {self.csv_fpath}...')
        with open(self.csv_fpath, newline='') as csvf:
            csvdict = csv.DictReader(csvf)
            keys = [k.lower() for k in csvdict.fieldnames]
            if not all([c.lower() in keys for c in self.cols]):
                raise MissingColumnsError(str(keys))
            for row in csvdict:
                row = dict([(rk.lower(), rv) for rk, rv in row.items()])
                sname = Roads2PopBatchProcessor._format_site_str(row['site'])
                self.inputd[sname] = row
                self.inputd[sname]['output_fname'] = f"{sname}Result.txt"
        print('done reading csv.')
        return self.inputd

    def _serialrun(self, **kwds):
        print(f'Running serial r2p job for: {self.site}...')
        output_path = os.path.join(self.output_path, f"{self.site}Result.txt")
        cmd_list = [self.cmdpath, output_path, self.lat, self.lon]
        proc = subprocess.run(cmd_list,
                              capture_output=False,
                              encoding='utf8',
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        print('process output:', proc.stdout)
        print(
            f'Done with RB Roads2Pop serial job. retcode: {
                proc.returncode}\r\n'
        )

    def _batchrun(self, **kwds):
        print('Starting RB Roads2Pop batch job...')
        for site, sdata in self.inputd.items():
            print(f'Running r2p job for: {site}...')
            output_path = os.path.join(self.output_path, sdata['output_fname'])
            cmd_list = [self.cmdpath, output_path, sdata['lat'], sdata['lon']]
            proc = subprocess.run(cmd_list,
                                  capture_output=False,
                                  encoding='utf8',
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
            print('process output:', proc.stdout)
            print(f'finished job. retcode: {proc.returncode}\r\n')
        print('Done with RB Roads2Pop batch jobs.')

    def run(self, **kwds):
        if self.mode == 'batch':
            self._batchrun()
        elif self.mode == 'serial':
            self._serialrun()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    config_method_group = parser.add_mutually_exclusive_group(required=True)
    config_method_group.add_argument(
        '--params',
        nargs='+',
        default=None,
        dest='str_params',
        help='(serial mode) input parameters for a serial R2P job. Must be written as a quoted tuple: "(site, lat, lon)"'
    )
    config_method_group.add_argument(
        '--csv',
        type=str,
        default=None,
        dest='csv',
        help='(batch mode) absolute path to csv file that contains (site, lat, lon) as columns.'
    )
    args = parser.parse_args()
    str_params = args.str_params
    mode = None
    if args.str_params is not None:
        mode = 'serial'
        str_params = ' '.join(args.str_params).replace(',', ', ')
        stmp = str_params.split(', ')
        stmp[0] = "'" + stmp[0].replace('(', '') + "'"
        str_params = '(' + ', '.join(stmp)
    elif args.csv is not None:
        mode = 'batch'
    r2pbatch = Roads2PopBatchProcessor(csv_fpath=args.csv,
                                       str_params=str_params,
                                       mode=mode)
    r2pbatch.run()
