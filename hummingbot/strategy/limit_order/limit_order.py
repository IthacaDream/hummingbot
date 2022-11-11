from decimal import Decimal
import logging

from hummingbot.core.event.events import OrderType
from hummingbot.strategy.market_trading_pair_tuple import MarketTradingPairTuple
from hummingbot.logger import HummingbotLogger
from hummingbot.strategy.strategy_py_base import StrategyPyBase
from hummingbot.core.data_type.common import (
    OrderType,
    PriceType,
    TradeType
)
from hummingbot.strategy.order_book_asset_price_delegate import OrderBookAssetPriceDelegate

hws_logger = None


class LimitOrder(StrategyPyBase):
    # We use StrategyPyBase to inherit the structure. We also
    # create a logger object before adding a constructor to the class.
    @classmethod
    def logger(cls) -> HummingbotLogger:
        global hws_logger
        if hws_logger is None:
            hws_logger = logging.getLogger(__name__)
        return hws_logger

    def __init__(self,
                 market_info: MarketTradingPairTuple,
                 ):

        super().__init__()
        self._market_info = market_info
        self._price_delegate = OrderBookAssetPriceDelegate(market_info.market, market_info.trading_pair)
        self._connector_ready = False
        self._order_completed = False
        self.add_markets([market_info.market])
        

    def format_status(self) -> str:
        """
        Method called by the `status` command. Generates the status report for this strategy.
        Simply outputs the balance of the specified asset on the exchange.
        """
        if not self._connector_ready:
            return "Exchange connector(s) are not ready."
        market, trading_pair, base_asset, quote_asset = self._market_info
        price = self._price_delegate.get_price_by_type(PriceType.MidPrice)
        base_balance = float(market.get_balance(base_asset))
        quote_balance = float(market.get_balance(quote_asset))
        available_base_balance = float(market.get_available_balance(base_asset))
        available_quote_balance = float(market.get_available_balance(quote_asset))
        base_value = base_balance * float(price)
        total_in_quote = base_value + quote_balance
        base_ratio = base_value / total_in_quote if total_in_quote > 0 else 0
        quote_ratio = quote_balance / total_in_quote if total_in_quote > 0 else 0
        data = [
            ["", base_asset, quote_asset],
            ["Total Balance", round(base_balance, 4), round(quote_balance, 4)],
            ["Available Balance", round(available_base_balance, 4), round(available_quote_balance, 4)],
            [f"Current Value ({quote_asset})", round(base_value, 4), round(quote_balance, 4)],
            ["Current %", f"{base_ratio:.1%}", f"{quote_ratio:.1%}"]
        ]
        return "\n".join(data)

    # After initializing the required variables, we define the tick method.
    # The tick method is the entry point for the strategy.
    def tick(self, timestamp: float):
        if not self._connector_ready:
            self._connector_ready = self._market_info.market.ready
            if not self._connector_ready:
                self.logger().warning(f"{self._market_info.market.name} is not ready. Please wait...")
                return
            else:
                self.logger().warning(f"{self._market_info.market.name} is ready. Trading started")

        if not self._order_completed:
            # The get_mid_price method gets the mid price of the coin and
            # stores it. This method is derived from the MarketTradingPairTuple class.
            mid_price = self._market_info.get_mid_price()

            # The buy_with_specific_market method executes the trade for you. This
            # method is derived from the Strategy_base class.
            order_id = self.buy_with_specific_market(
                self._market_info,  # market_trading_pair_tuple
                Decimal("0.005"),   # amount
                OrderType.LIMIT,    # order_type
                mid_price           # price
            )
            self.logger().info(f"Submitted limit buy order {order_id}")
            self._order_completed = True

    # Emit a log message when the order completes
    def did_complete_buy_order(self, order_completed_event):
        self.logger().info(f"Your limit buy order {order_completed_event.order_id} has been executed")
        self.logger().info(order_completed_event)
