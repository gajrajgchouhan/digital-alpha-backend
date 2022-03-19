import logging
from flask import Flask, request

from download_filings import download_fillings

app = Flask(__name__)
download = download_fillings()


@app.route("/create_dataset", methods=["POST"])
def create_dataset():
    body = request.json
    tickers = body["tickers"]  # list of tickers/cik ['AAPL', 'MSFT', 'GOOG'] etc.
    start = body["start"]  # '2019-01-01'
    end = body.get("end", "2022-01-01")  # '2020-01-01'
    forms = body["forms"]  # ["10-K", "10-Q", "8-K"]

    try:
        return download.download(tickers, start, end, forms), 200
    except Exception as e:
        logging.debug(e)
        return {"Error": "Something went wrong"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
