"""Vistas principales de GamerGear."""

from .afnd_visualizer import build_afnd_visualizer
from .alternatives import build_alternatives_view
from .delivery_location import build_delivery_location_view
from .home import build_home_view
from .login_view import build_login_view
from .order_review import build_order_review_view
from .orders import build_orders_view
from .placeholder import build_placeholder_view
from .product_detail import build_product_detail_view
from .products import build_products_view
from .profile import build_profile_view
from .tracking import build_tracking_view

__all__ = [
    "build_afnd_visualizer",
    "build_alternatives_view",
    "build_delivery_location_view",
    "build_home_view",
    "build_login_view",
    "build_order_review_view",
    "build_orders_view",
    "build_placeholder_view",
    "build_product_detail_view",
    "build_products_view",
    "build_profile_view",
    "build_tracking_view",
]
