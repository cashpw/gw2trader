import pandas as pd

# 'Listing fee'
fee_percent_on_list = 0.05
# 'Exchange fee'
fee_percent_on_sell = 0.10

def profit(buy_price_column: str, sell_price_column: str) -> pd.DataFrame:
    """Return sales profit; revenue, less trading post cuts."""

    return sell_price_column - \
        buy_price_column - \
        (fee_percent_on_list * sell_price_column) - \
        (fee_percent_on_sell * sell_price_column)
