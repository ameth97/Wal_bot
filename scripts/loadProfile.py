#!/usr/bin/env python
import sys
import pandas as pd

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = pd.read_excel(sys.argv[1])
        print(data)
        data.to_json(path_or_buf='data/profiles.json',orient='records')
    else:
        raise SystemExit("usage:  python loadProfile.py <Profilefilepath>")