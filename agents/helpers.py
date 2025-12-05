# Clara - Helpers pour agents
"""
Helpers génériques pour les agents, notamment pour les actions filesystem.
"""

from typing import Any, Dict, Optional
from drivers.fs_driver import FSDriver


# fs_driver sera injecté depuis run_clara.py ou api_server.py
_fs_driver: Optional[FSDriver] = None


def set_fs_driver(driver: FSDriver) -> None:
    """Configure le driver filesystem pour les helpers."""
    global _fs_driver
    _fs_driver = driver


def execute_fs_action(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Point d'entrée générique pour les actions filesystem.

    action: nom d'action (read_text, write_text, list_dir, etc.)
    params: dict d'arguments attendu par FSDriver
    """
    if _fs_driver is None:
        return {"ok": False, "error": "FSDriver not initialized"}

    try:
        if action == "read_text":
            content = _fs_driver.read_text(
                params["path"],
                encoding=params.get("encoding", "utf-8")
            )
            return {"ok": True, "content": content}

        if action == "write_text":
            _fs_driver.write_text(
                params["path"],
                params.get("content", ""),
                encoding=params.get("encoding", "utf-8"),
                overwrite=params.get("overwrite", True),
            )
            return {"ok": True, "message": f"File written: {params['path']}"}

        if action == "append_text":
            _fs_driver.append_text(
                params["path"],
                params.get("content", ""),
                encoding=params.get("encoding", "utf-8")
            )
            return {"ok": True, "message": f"Content appended to: {params['path']}"}

        if action == "read_bytes":
            content = _fs_driver.read_bytes(params["path"])
            return {"ok": True, "content": content.hex() if content else ""}

        if action == "write_bytes":
            content_hex = params.get("content", "")
            content = bytes.fromhex(content_hex) if content_hex else b""
            _fs_driver.write_bytes(
                params["path"],
                content,
                overwrite=params.get("overwrite", True),
            )
            return {"ok": True, "message": f"File written: {params['path']}"}

        if action == "list_dir":
            items = _fs_driver.list_dir(params.get("path", ""))
            return {
                "ok": True,
                "items": [item.__dict__ for item in items],
            }

        if action == "make_dir":
            _fs_driver.make_dir(
                params["path"],
                exist_ok=params.get("exist_ok", True)
            )
            return {"ok": True, "message": f"Directory created: {params['path']}"}

        if action == "move_path":
            _fs_driver.move_path(
                params["src"],
                params["dst"],
                overwrite=params.get("overwrite", False),
            )
            return {"ok": True, "message": f"Moved: {params['src']} -> {params['dst']}"}

        if action == "delete_path":
            _fs_driver.delete_path(params["path"])
            return {"ok": True, "message": f"Deleted: {params['path']}"}

        if action == "stat_path":
            info = _fs_driver.stat_path(params["path"])
            return {"ok": True, "info": info}

        if action == "search_text":
            results = _fs_driver.search_text(
                query=params["query"],
                start_relative=params.get("path", ""),
                max_files=params.get("max_files", 100),
                extensions=params.get("extensions"),
            )
            return {"ok": True, "results": results}

        return {"ok": False, "error": f"Unknown fs action: {action}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

