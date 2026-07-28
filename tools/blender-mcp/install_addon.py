"""Install / enable Blender MCP addon from this folder (headless-safe)."""
import bpy
import os
import sys

ADDON_MODULE = "blender_mcp_addon"
ADDON_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addon.py")
# Blender wants a unique module name under scripts/addons
USER_SCRIPTS = bpy.utils.user_resource("SCRIPTS", path="addons")
DST = os.path.join(USER_SCRIPTS, "blender_mcp_addon.py")


def main() -> None:
    if not os.path.isfile(ADDON_SRC):
        print(f"FAIL missing addon: {ADDON_SRC}")
        sys.exit(1)
    os.makedirs(USER_SCRIPTS, exist_ok=True)
    with open(ADDON_SRC, "rb") as f:
        data = f.read()
    with open(DST, "wb") as f:
        f.write(data)
    print(f"Wrote {DST} ({len(data)} bytes)")

    # Disable old if present, then enable
    for mod in ("blender_mcp_addon", "addon"):
        try:
            bpy.ops.preferences.addon_disable(module=mod)
        except Exception:
            pass
    try:
        bpy.ops.preferences.addon_enable(module="blender_mcp_addon")
        print("ENABLED blender_mcp_addon")
    except Exception as e:
        # Fallback: load from path once
        print(f"enable ops failed: {e}; trying import")
        import importlib.util

        spec = importlib.util.spec_from_file_location("blender_mcp_addon", DST)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["blender_mcp_addon"] = mod
        spec.loader.exec_module(mod)
        if hasattr(mod, "register"):
            mod.register()
        print("REGISTERED via import")

    bpy.ops.wm.save_userpref()
    print("SAVED user preferences")
    print("AIDLE_BLENDER_MCP_ADDON=PASS")


if __name__ == "__main__":
    main()
