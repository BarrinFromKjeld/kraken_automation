""""Kraken DCA application."""
from __future__ import annotations
import time

from typing import Any, Dict, List, TypedDict

import requests
from modules.kraken_requests import kraken_request
from modules.log import create_logger


OrderDict = TypedDict("OrderDict", {"pair": str, "amount": float})


logger = create_logger(__name__)


def _get_account_balance() -> Dict[str, Any]:
    return kraken_request("/0/private/Balance")


def _get_current_price(pair: str) -> float:
    data = {"pair": pair}
    return float(kraken_request("/0/public/Ticker", data=data)[pair]["a"][0])


def _buy(pair: str, amount: float) -> None:
    current_price = _get_current_price(pair)
    endpoint = "/0/private/AddOrder"
    data: Dict[str, str] = {
        "pair": pair,
        "ordertype": "market",
        "type": "buy",
        "volume": str(amount / current_price),
        "validate": "true",  # With this flag transactions are not executed
    }
    logger.info("buying with payload %s at %f", data, current_price)
    kraken_request(endpoint, data=data)


def _get_system_status() -> str:
    return kraken_request("/0/public/SystemStatus")["status"]


def _main() -> None:
    try:
        while True:
            api_status = _get_system_status()  # request 1
            if api_status == "online":
                break
            logger.warning("API is not online. Current status: %s. Trying again in 10 min.", api_status)
            time.sleep(600)
    except requests.HTTPError as exc:
        logger.warning("Cannot determine API status. Trying again in 10 min: %s", exc)
    account_balance = _get_account_balance()  # request 2
    orders: List[OrderDict] = [
        {"pair": "XETHZEUR", "amount": 25.0},  # buy 50 € worth of ETH
        {"pair": "XXBTZEUR", "amount": 25.0},  # buy 50 € worth of BTC
    ]
    summed_amount = sum([order["amount"] for order in orders])
    summed_amount += 0.01 * len(orders)  # add some buffer for slippage
    if float(account_balance["ZEUR"]) >= summed_amount:
        for i, order in enumerate(orders):
            if i > 5:
                # Buying requires 2 requests. If i == 6 we processed 6 orders which equals 12 requests. With the
                # additional 2 requests from get_system_status, get_account_balance we reach 14. Kraken allows 15
                # requests for basic users with a recovery rate of 0.33 req/sec. We could wait now for 3 seconds to
                # have again 2 requests available, but every subsequent order would need to wait for 6 seconds, so we
                # directly wait for 6 seconds, as this is not time critical.
                time.sleep(6)
            _buy(order["pair"], order["amount"])
    else:
        logger.warning("Cannot buy %f with %f funds available", summed_amount, account_balance["ZEUR"])


if __name__ == "__main__":
    try:
        _main()
    except Exception:  # pylint: disable=broad-except  # this is supposed to be a catch all for nicer error formatting
        logger.exception("Caught exception in main: ")
