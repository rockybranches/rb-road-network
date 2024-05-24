import os
import pandas as pd
import traceback

rb_data_path = os.getenv('RB_DATA')
cpop_path = os.path.join(rb_data_path, 'county_pop')


def list_csv_files():
    fpaths = [os.path.join(cpop_path, fn) for fn in os.listdir(cpop_path)]
    return fpaths


def load_fix_dfs():
    fpaths = list_csv_files()
    for fp in fpaths:
        print(f'loading {fp}...')
        df = pd.read_csv(fp)
        df = df[[c for c in df.columns if 'Unnamed:' not in c]]
        rcols = [k for k in df.columns if '20' in k]
        df.fillna('0', inplace=True)
        try:
            df[rcols] = df[rcols].applymap(lambda d: str(int(float(d))).replace(',', ''))
        except (AttributeError, ValueError):
            traceback.print_exc()
        df = df.astype(dict(zip(rcols, [int, ]*len(rcols))))
        df = df.astype({'County': str})
        df.to_csv(fp, index=False)
        print('...fixed and saved.')
    print('...done.')
    return fpaths


if __name__=='__main__':
    fpaths = load_fix_dfs()
    df_tmp = pd.read_csv(fpaths[0])
    print(df_tmp.head())
    
