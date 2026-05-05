from doctest import master

import pandas as pd
import requests
import ast
import time
import random
from pathlib import Path
import argparse

# User-Agent rotation
AGENTS = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def is_url_viable_fast(url_list_str, probe_bytes=2 ** 18):  # 256KB
    """Returns True if ANY URL viable. FAST 256KB probe, max 3 URLs."""
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': random.choice(AGENTS)})

        url_list = list(set(ast.literal_eval(url_list_str)))

        for url in url_list[:3]:  # First 3 URLs only
            try:
                resp = session.get(
                    url, stream=True,
                    timeout=(10, 20),
                    headers={'Accept': '*/*', 'Range': f'bytes=0-{probe_bytes - 1}'},
                    allow_redirects=True
                )

                if resp.status_code in (200, 206) and len(resp.content) > 1024:
                    print(f"{url.split('/')[-1]}: VIABLE")
                    session.close()
                    return True

                time.sleep(0.5)

            except:
                continue

        session.close()
        return False

    except:
        return False


def update_downloadable_column(master_path, output_path=None, probe_bytes=2 ** 18):
    """Update master DF: FALSE → TRUE where viable."""
    df = pd.read_excel(master_path)
    false_mask = df['Downloadable'] == False
    original_false = false_mask.sum()

    print(f"Initiating serialised scanning {original_false} rows flagged initially as Downloadable == FALSE... ")
    print(f"This is done to mimic human browsing and avoid ESGF mirror IP blocks when scraping the existence of many files")
    viable_count = 0

    for idx in df[false_mask].index:
        row = df.loc[idx]
        if is_url_viable_fast(row['HTTPServer'], probe_bytes):
            df.at[idx, 'Downloadable'] = True
            viable_count += 1

        time.sleep(random.uniform(2, 4))  # ESGF-safe

    print(f"Updated {viable_count}/{original_false} rows")

    if output_path is None:
        output_path = str(master_path).replace('.xlsx', '_updated.xlsx')

    df.to_excel(output_path, index=False)
    print(f"SAVED Dataframe with file probing results: {output_path}")
    return df


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Update Downloadable column')
    # parser.add_argument('master_file', help='Input spreadsheet')
    # parser.add_argument('-o', '--output', help='Output file')
    # parser.add_argument('--probe-size', type=int, default=2 ** 18, help='Probe size in bytes (default: 256KB)')
    # args = parser.parse_args()
    master_file = Path('/Users/leonardobertini/Desktop/ESGF_Downloads/DF_Downloadable_expc_epc100.xlsx')
    output_file = master_file
    probe_size = 2**18
    DF = pd.read_excel(master_file)
    false_count = (DF['Downloadable'] == False).sum()

    while false_count() > 0:
        print(f"Found files for which the Downloadable flag returned FALSE")
        print(f"Initiating gentle serialised scanning...")
        update_downloadable_column(master_file, output_file, probe_size)