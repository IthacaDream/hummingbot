import logging

from hummingbot.core.event.events import (
    BuyOrderCompletedEvent,
    BuyOrderCreatedEvent,
    MarketOrderFailureEvent,
    OrderCancelledEvent,
    OrderFilledEvent,
    SellOrderCompletedEvent,
    SellOrderCreatedEvent,
)
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase, Decimal, OrderType
from hummingbot.connector.utils import split_hb_trading_pair


class Script1(ScriptStrategyBase):

    # It is best to first use a paper trade exchange connector
    # while coding your strategy, once you are happy with it
    # then switch to real one.

    markets = {"binance_paper_trade": {"BTC-USDT"}}
    is_buy = True

    def on_tick(self):
        mid_price = self.connectors["binance_paper_trade"].get_mid_price("BTC-USDT")
        sell_price = self.connectors["binance_paper_trade"].get_price("BTC-USDT", False)
        buy_price = self.connectors["binance_paper_trade"].get_price("BTC-USDT", True)
        msg = f"Bitcoin mid_price: ${mid_price} buy_price: ${buy_price} sell_price: ${sell_price}"
        self.logger().info(msg)
        self.notify_hb_app_with_timestamp(msg)
        if self.is_buy:
            amount = Decimal("100") / sell_price
            self.buy("binance_paper_trade", "BTC-USDT", amount, OrderType.LIMIT, sell_price)
            self.is_buy = False

    def did_create_buy_order(self, event: BuyOrderCreatedEvent):
        """
        Method called when the connector notifies a buy order has been created
        """
        self.logger().info(logging.INFO, f"The buy order {event.order_id} has been created")

    def did_create_sell_order(self, event: SellOrderCreatedEvent):
        """
        Method called when the connector notifies a sell order has been created
        """
        self.logger().info(logging.INFO, f"The sell order {event.order_id} has been created")

    def did_fill_order(self, event: OrderFilledEvent):
        """
        Method called when the connector notifies that an order has been partially or totally filled (a trade happened)
        """
        # self.logger().info(logging.INFO, f"The order {event.order_id} has been filled")
        msg = (f"({event.trading_pair}) {event.trade_type.name} order (price: {event.price}) of {event.amount} "
               f"{split_hb_trading_pair(event.trading_pair)[0]} is filled.")
        self.log_with_clock(logging.INFO, msg)
        self.notify_hb_app_with_timestamp(msg)

    def did_fail_order(self, event: MarketOrderFailureEvent):
        """
        Method called when the connector notifies an order has failed
        """
        self.logger().info(logging.INFO, f"The order {event.order_id} failed")

    def did_cancel_order(self, event: OrderCancelledEvent):
        """
        Method called when the connector notifies an order has been cancelled
        """
        self.logger().info(f"The order {event.order_id} has been cancelled")

    def did_complete_buy_order(self, event: BuyOrderCompletedEvent):
        """
        Method called when the connector notifies a buy order has been completed (fully filled)
        """
        self.logger().info(f"The buy order {event.order_id} has been completed")

    def did_complete_sell_order(self, event: SellOrderCompletedEvent):
        """
        Method called when the connector notifies a sell order has been completed (fully filled)
        """
        self.logger().info(f"The sell order {event.order_id} has been completed")
