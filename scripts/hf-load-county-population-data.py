from datasets import load_dataset


def load_rb_county_pop_dataset():
    ds = load_dataset("rockybranches/county-population-data")
    return ds


if __name__=='__main__':
    ds = load_rb_county_pop_dataset()
    print('Dataset loaded: ', repr(ds)[:20], '...')
