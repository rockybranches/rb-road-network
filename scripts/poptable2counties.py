import re
import os
from typing import List
from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)


rb_data_dirpath = os.getenv('RB_DATA', '/mnt/c/Users/rcapps/Documents/rb_data')
output_dirpath = Path(rb_data_dirpath).joinpath('rb_output')


def find_counties(txt: str) -> List:
    return re.findall(r'\n(?!County)([A-Z]\w+)\s&', txt)


def get_txt(fname = 'KnoxEnterprises.txt'):
    global output_dirpath
    fpath = output_dirpath.joinpath(fname)
    logger.info(f'reading table from: "{fpath}" ...')
    txt = fpath.read_text()
    logger.info('...read table text successfully.')
    return txt


if __name__ == '__main__':
    prompt_text = 'Select one of the following options:'
    fpaths = list(output_dirpath.glob('*.txt'))
    options_str = '\n'.join([f'\t{i:02d} )\t{fpaths[i]}' for i in range(len(fpaths))])
    prompt_text = f'{prompt_text}{options_str}\n...: '
    ix_value = int(input(prompt_text))
    fname = fpaths[ix_value].name
    c_value = input(f'selected: {fname} ... Continue? [y/n]: ')
    if c_value == 'n':
        print('ok, exiting...')
        sys.exit(0)
    txt = get_txt(fname=fname)
    counties = find_counties(txt)
    print('"Name" IN (' + ",\n".join([f"'{c}'" for c in counties]).rstrip(',') + ')\n')
    print('...done.')
