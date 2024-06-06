import re
import requests
import logging

import pandas as pd
import numpy as np

from dataclasses import dataclass
from operator import attrgetter
from enum import Enum
from typing import List, Self, Optional
from gw2tpdb import Gw2TpDb
from gw2tpdb.api.history import HistoryEntry
from urllib.parse import urlencode
from bs4 import BeautifulSoup

gw2bltc_url="https://www.gw2bltc.com/en/tp/search"
stack_size = 250

# TODO: Move to separate file
def copper_to_gold_silver_copper(copper: int) -> tuple:
    """TODO"""

    gold = copper // 10000
    silver = (copper - (gold * 10000)) // 100

    return int(gold), int(silver), int(copper - (gold * 10000) - (silver * 100))

# TODO: Move to separate file
class Coins():
    """Represents a combination of gold, silver, and copper coins."""

    def __init__(self, copper: int = 0, silver: int = 0, gold: int = 0):
        """Initialize a representation of coins.

        - Coins(12345) implies 1 gold, 23 silver, and 45 copper
        - Coins(copper=45, silver=12) implies 0 gold, 12 silver, and 45 copper
        - Coins(gold=8) implies 8 gold, 0 silver, and 0 copper
        """

        if copper < 0 or silver < 0 or gold < 0:
            raise Exception("Cannot store negative coins.")

        if (silver == 0 and gold == 0) and copper > 0:
            self._gold, self._silver, self._copper = copper_to_gold_silver_copper(copper)
        else:
            self._gold = gold or 0
            self._silver = silver or 0
            self._copper = copper or 0

    def __repr__(self):
        """TODO"""
        return self._human_readable()

    def __str__(self):
        """TODO"""
        return self._human_readable()

    def __gt__(self, other: Self) -> bool:
        """Return true if A is > B."""

        return self.copper() > other.copper()

    def __ge__(self, other: Self) -> bool:
        """Return true if A is >= B."""

        return self.copper() >= other.copper()

    def __add__(self, other: Self) -> Self:
        """Return the sum of two Coins."""

        return Coins(self.copper() + other.copper())

    def __sub__(self, other: Self) -> Self:
        """Return the difference of two Coins."""

        return Coins(self.copper() - other.copper())

    def __mul__(self, other: int|float) -> Self:
        """Return the produt of OTHER and self."""

        return Coins(self.copper() * other)

    def _human_readable(self) -> str:
        """Return human-readable representation of coinage."""

        if self._gold == 0 and self._silver == 0:
            return f"{self._copper:>2}c"

        if self._gold == 0:
            return f"{self._silver:>2}s {self._copper:>2}c"

        return f"{self._gold: >2}g {self._silver: >2}s {self._copper: >2}c"

    def copper(self) -> int:
        """Return value in copper."""

        return self._copper + (self._silver * 100) + (self._gold * 10000)

# TODO: Move to separate file?
@dataclass
class Item():
    """TODO"""

    id: int
    name: str

# TODO: Move to separate file?
@dataclass
class DailyFlipReport():
    """TODO"""

    gw2bltc_url: str
    item_id: int
    item_name: str
    return_on_investment: float
    max_buy_count: float
    max_invest: Coins
    buy_price: Coins
    sell_price: Coins
    buy_volume: int
    sell_volume: int

# TODO: Move to separate file?
@dataclass
class Analysis():
    """TODO"""

    item: Item
    # TODO: Specify
    df: pd.DataFrame


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    filename="trader.log",
    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("---------")

def sort_history_by_timestamp(entries: List[HistoryEntry], reverse: bool = False) -> List[HistoryEntry]:
    """Sort ENTRIES by timestamp field."""

    return sorted(entries, key=attrgetter("utc_timestamp"), reverse=reverse)

def history_to_pandas(entries: List[HistoryEntry]) -> pd.DataFrame:
    """Return n-dimensional numpy array for ENTRIES."""

    return pd.DataFrame(entries, columns=["id",
                                     "buy_delisted",
                                     "buy_listed",
                                     "buy_price_avg",
                                     "buy_price_max",
                                     "buy_price_min",
                                     "buy_price_stdev",
                                     "buy_quantity_avg",
                                     "buy_quantity_max",
                                     "buy_quantity_min",
                                     "buy_quantity_stdev",
                                     "buy_sold",
                                     "buy_value",
                                     "count",
                                     "sell_delisted",
                                     "sell_listed",
                                     "sell_price_avg",
                                     "sell_price_max",
                                     "sell_price_min",
                                     "sell_price_stdev",
                                     "sell_quantity_avg",
                                     "sell_quantity_max",
                                     "sell_quantity_min",
                                     "sell_quantity_stdev",
                                     "sell_sold",
                                     "sell_value",
                                     "utc_timestamp",])

def copper_to_gold(df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
    """Convert copper values to gold.

    1 gold = 10000 copper."""

    for column_name in column_names:
        df[column_name] = df[column_name] / 100 / 100

    return df

def same_day_flip_profit(df: pd.DataFrame, buy_price_column_name: str, sell_price_column_name: str) -> pd.DataFrame:
    """TODO"""

    # 5% listing fee
    listing_fee = df[sell_price_column_name] * 0.05
    # 10% exchange fee
    exchange_fee = df[sell_price_column_name] * 0.1

    return df[sell_price_column_name] - \
        df[buy_price_column_name] - \
        listing_fee - \
        exchange_fee

def calc_profit(buy_price: int, sell_price: int) -> int:
    """Return revenue minus trading post cuts."""

    revenue = sell_price - buy_price
    # 5% listing fee
    listing_fee = sell_price * 0.05
    # 10% exchange fee
    exchange_fee = sell_price * 0.1

    return revenue - listing_fee - exchange_fee

db = Gw2TpDb(database_path="gw2trader.sqlite", auto_update=True)
#db.populate_items()

def analyze_daily_flip(item: Item, entries: List[HistoryEntry]) -> Analysis:
    """TODO"""

    moving_average_window = 14

    df = history_to_pandas(sort_history_by_timestamp(entries))

    df["buy_price_avg_-1stdev"] = df["buy_price_avg"] - (1 * df["buy_price_stdev"])
    #df["buy_price_avg_-2stdev"] = df["buy_price_avg"] - (2 * df["buy_price_stdev"])

    df["sell_price_avg_+1stdev"] = df["sell_price_avg"] + (1 * df["sell_price_stdev"])
    #df["sell_price_avg_+2stdev"] = df["sell_price_avg"] + (2 * df["sell_price_stdev"])

    """
    df["same_day_flip_profit"] = same_day_flip_profit(df,
                                    buy_price_column_name="buy_price_avg",
                                    sell_price_column_name="sell_price_avg")
    """
    df["same_day_flip_profit_1stdev"] = same_day_flip_profit(df,
                                    buy_price_column_name="buy_price_avg_-1stdev",
                                    sell_price_column_name="sell_price_avg_+1stdev")
    """
    df["same_day_flip_profit_2stdev"] = same_day_flip_profit(df,
                                    buy_price_column_name="buy_price_avg_-2stdev",
                                    sell_price_column_name="sell_price_avg_+1stdev")
    """
    #df["same_day_flip_roi"] = (df["same_day_flip_profit"] + df["buy_price_avg"]) / df["buy_price_avg"]
    df["same_day_flip_1stdev_roi"] = (df["same_day_flip_profit_1stdev"] + df["buy_price_avg_-1stdev"]) / df["buy_price_avg_-1stdev"]
    #df["same_day_flip_2stdev_roi"] = (df["same_day_flip_profit_2stdev"] + df["buy_price_avg_-2stdev"]) / df["buy_price_avg_-2stdev"]

    # Moving averages
    df[f"buy_sold_{moving_average_window}d_ma"] = df["buy_sold"].rolling(moving_average_window).mean()
    #df["buy_value_30d_ma"] = df["buy_value"].rolling(30).mean()

    #df["sell_sold_7d_ma"] = df["sell_sold"].rolling(7).mean()
    #df["sell_sold_14d_ma"] = df["sell_sold"].rolling(14).mean()
    #df["sell_sold_30d_ma"] = df["sell_sold"].rolling(30).mean()
    df[f"sell_sold_{moving_average_window}d_ma"] = df["sell_sold"].rolling(moving_average_window).mean()

    #df["sell_value_{moving_average_window}d_ma"] = df["sell_value"].rolling(moving_average_window).mean()

    #df["same_day_flip_roi_30d_ma"] = df["same_day_flip_roi"].rolling(30).mean()
    #df["same_day_flip_1stdev_roi_7d_ma"] = df["same_day_flip_1stdev_roi"].rolling(7).mean()
    #df["same_day_flip_1stdev_roi_14d_ma"] = df["same_day_flip_1stdev_roi"].rolling(14).mean()
    #df["same_day_flip_1stdev_roi_30d_ma"] = df["same_day_flip_1stdev_roi"].rolling(30).mean()
    df[f"same_day_flip_1stdev_roi_{moving_average_window}d_ma"] = df["same_day_flip_1stdev_roi"].rolling(moving_average_window).mean()
    #df["same_day_flip_2stdev_roi_30d_ma"] = df["same_day_flip_2stdev_roi"].rolling(30).mean()

    df["10%_sell_sold"] = df["sell_sold"] * 0.1
    #df["10%_sell_sold_7d_ma"] = df["10%_sell_sold"].rolling(7).mean()
    #df["10%_sell_sold_14d_ma"] = df["10%_sell_sold"].rolling(14).mean()
    df[f"10%_sell_sold_{moving_average_window}d_ma"] = df["10%_sell_sold"].rolling(moving_average_window).mean()
    #df["10%_sell_sold_30d_stdev"] = df["10%_sell_sold"].rolling(30).std()
    #df["10%_sell_sold_30d_ma+2stdev"] = df["10%_sell_sold_30d_ma"] + (2 * df["10%_sell_sold_30d_stdev"])
    #df["10%_sell_sold_30d_ma-2stdev"] = df["10%_sell_sold_30d_ma"] - (2 * df["10%_sell_sold_30d_stdev"])

    #df["10%_sell_value"] = df["sell_value"] * 0.1
    #df["10%_sell_value_30d_ma"] = df["10%_sell_value"].rolling(30).mean()
    #df["10%_sell_value_30d_stdev"] = df["10%_sell_value"].rolling(30).std()
    #df["10%_sell_value_30d_ma+2stdev"] = df["10%_sell_value_30d_ma"] + (2 * df["10%_sell_value_30d_stdev"])
    #df["10%_sell_value_30d_ma-2stdev"] = df["10%_sell_value_30d_ma"] - (2 * df["10%_sell_value_30d_stdev"])

    #df["roi_value_on_10%_sell_value"] = (df["10%_sell_value"] * df["same_day_flip_roi"]) - df["10%_sell_value"]
    #df["roi_value_on_10%_sell_value_30d_rolling_sum"] = df["roi_value_on_10%_sell_value"].rolling(30).sum()
    #df["roi_value_on_10%_sell_value_30d_rolling_std"] = df["roi_value_on_10%_sell_value"].rolling(30).std()

    # Expected total profit if you sold 10% of volume every day for 30 days
    #df["roi_value_on_10%_sell_value_30d_rolling_sum_30d_ma"] = df["roi_value_on_10%_sell_value_30d_rolling_sum"].rolling(30).mean()

    return Analysis(item, df[[
        #"buy_sold",
        f"buy_sold_{moving_average_window}d_ma",
        #"buy_value",
        #"buy_value_30d_ma",
        #"buy_price_avg",
        "buy_price_avg_-1stdev",
        #"buy_price_avg_-2stdev",

        #"sell_sold",
        #"sell_sold_7d_ma",
        #"sell_sold_14d_ma",
        f"sell_sold_{moving_average_window}d_ma",
        #"sell_value",
        #"sell_value_30d_ma",
        #"sell_price_min",
        #"sell_price_avg",
        "sell_price_avg_+1stdev",
        #"sell_price_avg_+2stdev",

        #"buy_price_avg_-2stdev",
        #"sell_price_avg_+2stdev",

        #"same_day_flip_profit",
        #"same_day_flip_roi",
        #"same_day_flip_roi_30d_ma",
        #"same_day_flip_1stdev_roi_7d_ma",
        #"same_day_flip_1stdev_roi_14d_ma",
        f"same_day_flip_1stdev_roi_{moving_average_window}d_ma",
        #"same_day_flip_2stdev_roi_30d_ma",

        #"10%_sell_sold",
        #"10%_sell_sold_30d_ma-2stdev",
        #"10%_sell_sold_7d_ma",
        #"10%_sell_sold_14d_ma",
        f"10%_sell_sold_{moving_average_window}d_ma",
        #"10%_sell_sold_30d_ma+2stdev",
        #"10%_sell_value",
        #"10%_sell_value_30d_ma-2stdev",
        #"10%_sell_value_30d_ma",
        #"10%_sell_value_30d_ma+2stdev",
        #"roi_value_on_10%_sell_value",
        #"roi_value_on_10%_sell_value_30d_rolling_sum",
        #"roi_value_on_10%_sell_value_30d_rolling_std",
        #"roi_value_on_10%_sell_value_30d_rolling_sum_30d_ma",
    ]])

def analysis_to_daily_flip_report(analysis: Analysis) -> DailyFlipReport:
    """TODO"""

    gw2bltc_url = f"https://www.gw2bltc.com/en/item/{analysis.item.id}"
    buy_volume, buy_price, sell_volume, sell_price, roi, ten_percent_sold_count = analysis.df.iloc[-1]
    max_buy_count = ten_percent_sold_count if roi > 1.0 else 0

    return DailyFlipReport(
        gw2bltc_url=gw2bltc_url,
        item_id=analysis.item.id,
        item_name=analysis.item.name,
        return_on_investment=roi,
        sell_volume=sell_volume,
        buy_volume=buy_volume,
        max_buy_count=max_buy_count,
        buy_price=Coins(buy_price),
        max_invest=Coins(buy_price * max_buy_count),
        sell_price=Coins(sell_price),
    )


def print_flip_plan(items: List[Item], min_sell_volume: int = 0, min_buy_volume: int = 0, min_buy_count: int = 0, min_buy_price: Coins = Coins()) -> None:
    """Print a flipping buy/sell plan for ITEMS."""

    def remove_rows_lt(df: pd.DataFrame, column_name: str, min_quantity: float) -> pd.DataFrame:
        """Remove rows for which df.column_name < min_quantity is true."""

        if df[df[column_name] < min_quantity].empty:
            return df
        items_to_be_removed = df[df[column_name] < min_quantity]["item_name"]

        logger.debug(f"Removed {len(items_to_be_removed)} items ({column_name} < {min_quantity}): {', '.join(items_to_be_removed)}")

        return df[df[column_name] >= min_quantity]

    entries_opt = db.get_dailies(list(map(lambda item: item.id, items)))
    if entries_opt is None:
        logger.debug(f"History entries empty")
        return None
    entries = entries_opt

    df = pd.DataFrame([report.__dict__ for report in map(analysis_to_daily_flip_report, map(lambda item: analyze_daily_flip(item, entries[item.id]), items))])
    df = remove_rows_lt(df, "return_on_investment", 1)
    df = remove_rows_lt(df, "sell_volume", min_sell_volume)
    df = remove_rows_lt(df, "buy_volume", min_buy_volume)
    df = remove_rows_lt(df, "max_buy_count", min_buy_count)
    df = remove_rows_lt(df, "buy_price", min_buy_price)
    if df.empty:
        print("Preconditions eliminated all candidate items. No profitable flips.")
        return None

    df=df.fillna(0)

    # Sort by return on investment (ROI)
    df.sort_values(by="return_on_investment", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    df["roi%"] = (df["return_on_investment"] - 1.0) * 100
    #df["max_buy_stacks"] = df["max_buy_count"] / stack_size
    df["buy_stacks"] = (df["max_buy_count"] / stack_size).apply(np.floor)
    df["buy_stack_price"] = df["buy_price"] * stack_size
    df["total_buy_price"] = df["buy_price"] * stack_size * df["buy_stacks"]
    df["sell_stack_price"] = df["sell_price"] * stack_size
    #df["max_invest_cum_sum"] = df["max_invest"].cumsum()
    df["invest"] = df["buy_price"] * df["buy_stacks"] * stack_size
    df["invest_cum_sum"] = df["invest"].cumsum()

    #out_of_money_row_index = df[df["max_invest_cum_sum"] >= budget].index[0]
    #out_of_money_row_index = None if df[df["invest_cum_sum"] >= budget].empty else df[df["invest_cum_sum"] >= budget].index[0]

    #print(f"Given a budget of {budget}, you should flip:")
    with pd.option_context("display.max_rows", None, "display.max_columns", None, "display.max_colwidth", None, "display.width", None):
        #print(df.loc[:out_of_money_row_index][[
        print(df[[
            #"item_id",
            "item_name",
            "gw2bltc_url",
            "roi%",
            #"max_buy_count",
            #"max_buy_stacks",
            "buy_stacks",
            #"max_invest",
            "buy_price",
            "buy_stack_price",
            "total_buy_price",
            "sell_price",
            "sell_stack_price",
            "invest_cum_sum"
            #"invest",
        ]])
def get_top_sold_items(count: int = 200, deadline_seconds: int = 5, page: int = 1) -> Optional[List[Item]]:
    """Return most sold items as known by GW2BLTC."""

    params = {
        "ipg": count,
        "sort": "sold-day",
        "page": page,
    }

    try:
        url = f"{gw2bltc_url}?{urlencode(params)}"
        response = requests.get(url, timeout=deadline_seconds)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        """
        with open("top_sold.html", "r") as f:
            soup = BeautifulSoup(f, 'html.parser')
        """

        # Use of `body` instead of `tbody` is intentional.
        # GW2BLTC uses invalid HTML
        items = soup.select(".table-result body .td-name > a")

        def _link_to_item(link) -> Item:
            """TODO"""

            href = link.get("href")
            item_id = int(re.search(".*item/(\d*)", href).group(1))
            item_name = link.contents[0]

            return Item(
                id=item_id,
                name=item_name)

        return list(map(_link_to_item, items))
    except requests.exceptions.Timeout as e:
        logger.error(f"Timed out (deadline={deadline_seconds} seconds) getting '{url}': {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting '{url}': {e}")

    return None

def get_top_1000_sold_items_or_quit() -> List[Item]:
    """TODO"""

    top_sold_items = []
    for top_sold_items_opt in [
            get_top_sold_items(200, page=1),
            get_top_sold_items(200, page=2),
            get_top_sold_items(200, page=3),
            get_top_sold_items(200, page=4),
            get_top_sold_items(200, page=5),
    ]:
        if top_sold_items_opt is None:
            logger.debug("Some top sold items missing")
            quit()

        top_sold_items += top_sold_items_opt

    return top_sold_items

def save_item_list(path: str, items: List[Item]) -> None:
    """TODO"""

    with open(path, "w") as f:
        f.write("[\n")
        for item in items:
            id = item.id
            name = item.name.replace('"', '\\"')
            f.write(f'    Item(id={id}, name="{name}"),\n')
        f.write("]")
    logger.debug(f"Wrote items to {path}")

#top_sold_items = get_top_1000_sold_items_or_quit()
#save_item_list("items.py", top_sold_items)
#quit()

print_flip_plan(min_buy_count=stack_size,
                min_buy_price=Coins(5),
                # Use stack_size*10 so our min 10%-of-volume is likely to be >1 stack
                min_buy_volume=stack_size*10,
                min_sell_volume=stack_size*10,
                items=get_top_1000_sold_items_or_quit())
