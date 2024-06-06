import logging

import pandas as pd
import numpy as np

from dataclasses import dataclass
from operator import attrgetter
from enum import Enum
from typing import List
from gw2tpdb import Gw2TpDb
from gw2tpdb.api.history import HistoryEntry

# TODO:
#
# Answer the following for a given ItemId:
#
# 1. What's the expected return on investment (ROI) percentage should I expect for same-day flips?
#
#    - Use 30 day moving averages data
#    - Calculate at both:
#      - Buy at -0 standard deviations and sell at +0 standard deviations
#      - Buy at -1 standard deviations and sell at +1 standard deviations
#      - Buy at -2 standard deviations and sell at +2 standard deviations
#
# 2. What's the ceiling on gold invested?
#
#    - Assume I can buy and sell 5% of the daily volume
#    - Assume I can buy and sell 10% of the daily volume
#    - Integrate standard deviations here as well
#
# 3. What is my target entry (buy) price?
# 4. What is my target exit (sell) price?
#
# Then stack-rank multiple ItemIds by those ROI% and invest gold in descending order
#
# Example:
#
# If I have 50 gold, and the stack rank comes out to:
#
# | Item | ROI  | Daily Investment Ceiling (gold) | Buy price (copper) | Sell price (copper) |
# |------+------+---------------------------------+--------------------+---------------------|
# | Foo  | 1.10 | 30                              | ?                  | ?                   |
# | Bar  | 1.07 | 15                              | ?                  | ?                   |
# | Baz  | 1.05 | 30                              | ?                  | ?                   |
# | Laz  | 1.02 | 55                              | ?                  | ?                   |
#
# Then I should flip (1) 30 gold of Foo, (2) 15 gold of Bar, (3) 5 gold of Baz, and (4) 0 gold of Laz.
#
# Create a function to print "don't make me think"-style instructions which, using the example results
# from above, would exclude Laz.
#
# Example:
#
# >>> flip_plan(...)
# | Item | Buy quantity | Buy price (unit) | Buy quantity (stacks) | Buy price (per stack) | Sell price |
# |------+--------------+------------------+-----------------------+-----------------------+------------|
# | ...  | ...          | ...              | ...                   | ...                   | ...        |
# | ...  | ...          | ...              | ...                   | ...                   | ...        |
# | ...  | ...          | ...              | ...                   | ...                   | ...        |

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

    item_id: int
    item_name: str
    return_on_investment: float
    max_buy_count: float
    max_gold_invest: float

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

db = Gw2TpDb(database_path="/tmp/gw2trader.sqlite", auto_update=True)
#db.populate_items()

def analyze_daily_flip(item: Item) -> Analysis:
    """TODO"""

    entries_opt = db.get_daily(item.id)
    if entries_opt is None:
        logger.debug(f"History entries empty for {item.id}")
        quit()

    entries = entries_opt

    df = history_to_pandas(sort_history_by_timestamp(entries))

    df["buy_price_avg_-1stdev"] = df["buy_price_avg"] - (1 * df["buy_price_stdev"])
    df["buy_price_avg_-2stdev"] = df["buy_price_avg"] - (2 * df["buy_price_stdev"])

    df["sell_price_avg_+1stdev"] = df["sell_price_avg"] + (1 * df["sell_price_stdev"])
    df["sell_price_avg_+2stdev"] = df["sell_price_avg"] + (2 * df["sell_price_stdev"])

    """
    add_same_day_flip_profit_column(df,
                                    buy_price_column_name="buy_price_avg_-2stdev",
                                    sell_price_column_name="sell_price_avg_+2stdev")
    """
    df["same_day_flip_profit"] = same_day_flip_profit(df,
                                    buy_price_column_name="buy_price_avg",
                                    sell_price_column_name="sell_price_avg")
    df["same_day_flip_profit_1stdev"] = same_day_flip_profit(df,
                                    buy_price_column_name="buy_price_avg_-1stdev",
                                    sell_price_column_name="sell_price_avg_+1stdev")
    df["same_day_flip_profit_2stdev"] = same_day_flip_profit(df,
                                    buy_price_column_name="buy_price_avg_-2stdev",
                                    sell_price_column_name="sell_price_avg_+1stdev")
    df["same_day_flip_roi"] = (df["same_day_flip_profit"] + df["buy_price_avg"]) / df["buy_price_avg"]
    df["same_day_flip_1stdev_roi"] = (df["same_day_flip_profit_1stdev"] + df["buy_price_avg_-1stdev"]) / df["buy_price_avg_-1stdev"]
    df["same_day_flip_2stdev_roi"] = (df["same_day_flip_profit_2stdev"] + df["buy_price_avg_-2stdev"]) / df["buy_price_avg_-2stdev"]

    # Moving averages
    df["buy_sold_30d_ma"] = df["buy_sold"].rolling(30).mean()
    df["buy_value_30d_ma"] = df["buy_value"].rolling(30).mean()
    df["sell_sold_30d_ma"] = df["sell_sold"].rolling(30).mean()
    df["sell_value_30d_ma"] = df["sell_value"].rolling(30).mean()
    df["same_day_flip_roi_30d_ma"] = df["same_day_flip_roi"].rolling(30).mean()
    df["same_day_flip_1stdev_roi_30d_ma"] = df["same_day_flip_1stdev_roi"].rolling(30).mean()
    df["same_day_flip_2stdev_roi_30d_ma"] = df["same_day_flip_2stdev_roi"].rolling(30).mean()

    df["10%_sell_sold"] = df["sell_sold"] * 0.1
    df["10%_sell_sold_30d_ma"] = df["10%_sell_sold"].rolling(30).mean()
    df["10%_sell_sold_30d_stdev"] = df["10%_sell_sold"].rolling(30).std()
    df["10%_sell_sold_30d_ma+2stdev"] = df["10%_sell_sold_30d_ma"] + (2 * df["10%_sell_sold_30d_stdev"])
    df["10%_sell_sold_30d_ma-2stdev"] = df["10%_sell_sold_30d_ma"] - (2 * df["10%_sell_sold_30d_stdev"])
    df["10%_sell_value"] = df["sell_value"] * 0.1
    df["10%_sell_value_30d_ma"] = df["10%_sell_value"].rolling(30).mean()
    df["10%_sell_value_30d_stdev"] = df["10%_sell_value"].rolling(30).std()
    df["10%_sell_value_30d_ma+2stdev"] = df["10%_sell_value_30d_ma"] + (2 * df["10%_sell_value_30d_stdev"])
    df["10%_sell_value_30d_ma-2stdev"] = df["10%_sell_value_30d_ma"] - (2 * df["10%_sell_value_30d_stdev"])

    df["roi_value_on_10%_sell_value"] = (df["10%_sell_value"] * df["same_day_flip_roi"]) - df["10%_sell_value"]
    df["roi_value_on_10%_sell_value_30d_rolling_sum"] = df["roi_value_on_10%_sell_value"].rolling(30).sum()
    df["roi_value_on_10%_sell_value_30d_rolling_std"] = df["roi_value_on_10%_sell_value"].rolling(30).std()

    # Expected total profit if you sold 10% of volume every day for 30 days
    #
    # 30dma return on selling 10% of
    df["roi_value_on_10%_sell_value_30d_rolling_sum_30d_ma"] = df["roi_value_on_10%_sell_value_30d_rolling_sum"].rolling(30).mean()

    copper_to_gold(df, [
        "buy_value",
        "buy_value_30d_ma",
        "buy_price_avg",
        "buy_price_max",
        "buy_price_min",
        "buy_price_stdev",

        "sell_value",
        "sell_value_30d_ma",
        "sell_price_avg",
        "sell_price_max",
        "sell_price_min",
        "sell_price_stdev",

        "buy_price_avg_-2stdev",
        "sell_price_avg_+2stdev",

        "10%_sell_value",
        "10%_sell_value_30d_ma-2stdev",
        "10%_sell_value_30d_ma",
        "10%_sell_value_30d_ma+2stdev",
        "roi_value_on_10%_sell_value",
        "roi_value_on_10%_sell_value_30d_rolling_sum",
        "roi_value_on_10%_sell_value_30d_rolling_std",
        "roi_value_on_10%_sell_value_30d_rolling_sum_30d_ma",

        "same_day_flip_profit",
    ])
    return Analysis(item, df[[
        #"buy_sold",
        #"buy_sold_30d_ma",
        #"buy_value",
        #"buy_value_30d_ma",
        "buy_price_avg",

        #"sell_sold",
        #"sell_sold_30d_ma",
        #"sell_value",
        #"sell_value_30d_ma",
        "sell_price_avg",
        #"sell_price_min",

        #"buy_price_avg_-2stdev",
        #"sell_price_avg_+2stdev",

        #"same_day_flip_profit",
        "same_day_flip_roi",
        "same_day_flip_roi_30d_ma",
        "same_day_flip_1stdev_roi_30d_ma",
        "same_day_flip_2stdev_roi_30d_ma",

        #"10%_sell_sold",
        #"10%_sell_sold_30d_ma-2stdev",
        "10%_sell_sold_30d_ma",
        #"10%_sell_sold_30d_ma+2stdev",
        #"10%_sell_value",
        #"10%_sell_value_30d_ma-2stdev",
        "10%_sell_value_30d_ma",
        #"10%_sell_value_30d_ma+2stdev",
        #"roi_value_on_10%_sell_value",
        #"roi_value_on_10%_sell_value_30d_rolling_sum",
        #"roi_value_on_10%_sell_value_30d_rolling_std",
        #"roi_value_on_10%_sell_value_30d_rolling_sum_30d_ma",
    ]])

def analysis_to_daily_flip_report(analysis: Analysis) -> DailyFlipReport:
    """TODO"""

    roi, ten_percent_sold_count, ten_percent_sold_value = analysis.df.iloc[-1]

    return DailyFlipReport(
        item_id=analysis.item.id,
        item_name=analysis.item.name,
        return_on_investment=roi,
        max_buy_count=ten_percent_sold_count if roi > 1.0 else 0,
        max_gold_invest=ten_percent_sold_value if roi > 1.0 else 0,
    )

iron_ingot_analysis = analyze_daily_flip(Item(id=19683, name="Iron Ingot"))
piece_of_candy_corn_analysis = analyze_daily_flip(Item(id=36041, name="Piece of Candy Corn"))

"""
df = pd.DataFrame([report.__dict__ for report in [
    analysis_to_daily_flip_report(iron_ingot_analysis),
    analysis_to_daily_flip_report(piece_of_candy_corn_analysis),
]])
df["return_on_investment_percent"] = (df["return_on_investment"] - 1.0) * 100
df.sort_values(by="return_on_investment")
with pd.option_context("display.max_rows", None):
    print(df[[
        "item_id",
        "item_name",
        "return_on_investment_percent",
        "max_buy_count",
        "max_gold_invest",
    ]])
"""

with pd.option_context("display.max_rows", None):
    print(piece_of_candy_corn_analysis.df[-40:])
print(calc_profit(110, 140))
