"""Local in-process authoritative World Commit POC (G6-001 M1).

Not production multiplayer. No public bind, no Nakama/Colyseus, no cloud.
"""

from .server import WorldAuthorityServer
from .client_sim import ClientMirror

__all__ = ["WorldAuthorityServer", "ClientMirror"]
