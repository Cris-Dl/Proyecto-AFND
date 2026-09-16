"""Vistas principales de GamerGear."""

from .afnd_visualizer import build_afnd_visualizer
from .home import build_home_view
from .login_view import build_login_view
from .order_review import build_order_review_view
from .placeholder import build_placeholder_view
from .product_detail import build_product_detail_view
from .products import build_products_view
from .profile import build_profile_view

__all__ = [
    "build_afnd_visualizer",
    "build_home_view",
    "build_login_view",
    "build_order_review_view",
    "build_placeholder_view",
    "build_product_detail_view",
    "build_products_view",
    "build_profile_view",
]
