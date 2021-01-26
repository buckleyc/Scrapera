import csv
import json
import os
import urllib.request
import zlib


class YahooScraper:
    """
    Scraper for Stock Market derived from Yahoo API
    """

    @staticmethod
    def _fetch_values(
        ticker: str, interval: str = "2m", range_of_data: str = "1d", proxy: dict = None
    ) -> tuple:

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,"
            "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
            "cache-control": "max-age=0",
            "dnt": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
        }

        request = urllib.request.Request(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?region=US&lang=en-US&includePrePost=false&"
            f"interval={interval}&useYfid=true&range={range_of_data}&corsDomain=finance.yahoo.com&.tsrc=finance",
            headers=headers,
        )

        if proxy:
            handler = urllib.request.ProxyHandler(proxy)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        content = urllib.request.urlopen(request)
        decompressed_data = zlib.decompress(content.read(), 16 + zlib.MAX_WBITS)
        json_data = json.loads(decompressed_data)

        high = json_data["chart"]["result"][0]["indicators"]["quote"][0]["high"]
        low = json_data["chart"]["result"][0]["indicators"]["quote"][0]["low"]
        open_ = json_data["chart"]["result"][0]["indicators"]["quote"][0]["open"]
        volume = json_data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
        close = json_data["chart"]["result"][0]["indicators"]["quote"][0]["close"]

        return high, low, open_, volume, close

    def scrape(
        self,
        ticker: str,
        interval: str = "2m",
        range_of_data: str = "1d",
        out_path: str = None,
        proxy: dict = None,
    ) -> None:
        """
        ticker: str, Name of the share. Example: AMZN (Amazon)
        interval: str, Intervals after which to scrape stocks data.
            Must be one of 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        range_of_data: str, Range of data to be scraped.
            Must be one of 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y
        out_path: str, Path to output directory
        proxy: dict, A dictionary consisting of proxy information for http/https proxies
        """

        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory received"

        ranges = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"]
        assert range_of_data in ranges, f"Invalid range: Must belong to {','.join(ranges)}"
        intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        assert interval in intervals, f"Invalid interval: Must belong to {','.join(intervals)}"

        data = self._fetch_values(ticker, interval, range_of_data, proxy)

        csv_file_name = f"{ticker}_stack_data.csv"
        csv_file = open(
            os.path.join('' if out_path is None else out_path, csv_file_name),
            "w+",
            newline="",
        )
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(["high", "low", "open", "volume", "close"])
        for i in zip(*data):
            writer.writerow(i)
