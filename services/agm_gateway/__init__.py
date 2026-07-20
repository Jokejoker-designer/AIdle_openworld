"""Provider-neutral Paid AGM trusted gateway (G5-001).

FixtureProvider only by default. No outbound network. No real credentials.
"""

from .gateway import GatewayService
from .errors import ErrorCategories

__all__ = ["GatewayService", "ErrorCategories"]

__version__ = "0.1.0"
