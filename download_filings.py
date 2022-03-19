import logging
import re
import pandas as pd
from sec_edgar_downloader import Downloader
import os
from pathlib import Path
from tqdm.auto import tqdm
import shutil
import parse_10q
import parse_form


class download_fillings:
    def __init__(self):
        logging.basicConfig(filename="download_fillings.log", level=logging.DEBUG)

        try:
            shutil.rmtree("./download_filings")
        except Exception as e:
            print(e)

        os.makedirs("./download_filings", exist_ok=False)
        self.dl = Downloader("./download_filings")
        self.FOLDER_PATH = "download_filings/sec-edgar-filings"
        self.PATTERN_OF_PATH = rf"{self.FOLDER_PATH}/(.*?)/(\d{{1,2}}-[QK])/(\d+-\d{{2}}-\d+)/full-submission.txt"

    def download(self, tickers, start, end, forms):
        for ticker in tickers:
            for form in tqdm(forms, total=len(forms), desc="Downloading forms", leave=False):
                logging.debug(
                    (
                        "Downloaded",
                        self.dl.get(
                            form, ticker, after=start, before=end, include_amends=False, download_details=False
                        ),
                        "fillings",
                    )
                )

        dataset = []
        for path in Path(self.FOLDER_PATH).glob("**/*.txt"):
            CIK, form_number, ASN = re.findall(self.PATTERN_OF_PATH, str(path))[0]
            logging.debug(f"{CIK}, {form_number}, {ASN}")
            filling_txt = open(path).read()
            if form_number == "10-Q":
                section_dict = parse_10q.parse_form(filling_txt)
            elif form_number == "10-K":
                section_dict = parse_form.parse_form(filling_txt)
            else:
                continue

            dataset.append({"cik_or_ticker": CIK, "form_number": form_number, "asn": ASN, "parsed": section_dict})

        return pd.DataFrame.from_dict(dataset).to_csv(None, index=False)
