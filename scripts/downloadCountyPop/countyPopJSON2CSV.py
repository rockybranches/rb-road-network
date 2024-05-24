import sys
import json
import pandas as pd

if __name__=='__main__':
    fname = sys.argv[1]
    print(f'input_fname={fname} ...')
    vals = []
    with open(fname, 'r') as fp:
        vals = json.load(fp)["valueRanges"][0]["values"]
    fname_out = fname.replace(".json", ".csv")
    df = pd.DataFrame(vals[1:], columns=vals[0])
    df.to_csv(fname_out, index=False)
    print(f'...saved to {fname_out}\n')
