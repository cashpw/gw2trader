import re
import requests
import logging

from typing import List, Optional
from item import Item
from urllib.parse import urlencode
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_top_sold_items(count: int = 200, deadline_seconds: int = 20, page: int = 1) -> Optional[List[Item]]:
    """Return most sold items as known by gw2bltc.com."""

    gw2bltc_url="https://www.gw2bltc.com/en/tp/search"
    params = {
        "ipg": count,
        "sort": "sold-day",
        "page": page,
    }
    url = f"{gw2bltc_url}?{urlencode(params)}"

    try:
        response = requests.get(url, timeout=deadline_seconds)
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        logger.error(f"Timed out (deadline={deadline_seconds} seconds) getting '{url}': {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting '{url}': {e}")
        return None


    soup = BeautifulSoup(response.text, 'html.parser')
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

def get_top_1000_sold_items() -> Optional[List[Item]]:
    """Return list of top-1000 most-sold items from gw2bltc.com."""

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
            return None

        top_sold_items += top_sold_items_opt

    return top_sold_items
