"""Quick check: is Blender MCP socket listening on 9876?"""
import socket
import sys

HOST = "127.0.0.1"
PORT = int(__import__("os").environ.get("BLENDER_PORT", "9876"))


def main() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        s.connect((HOST, PORT))
    except OSError as e:
        print(f"BLENDER_MCP_PORT={PORT} status=DOWN err={e}")
        print("Open Blender → N sidebar → BlenderMCP → Connect")
        return 1
    finally:
        s.close()
    print(f"BLENDER_MCP_PORT={PORT} status=UP host={HOST}")
    print("Grok can use blender MCP tools now (restart Grok if tools missing).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
