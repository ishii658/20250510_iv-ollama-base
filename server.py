"""FastAPIのメモ保存サーバー."""

import traceback
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from db import Db, MarkdownDataType

app = FastAPI()

# モダンなパス構築
dist_dir = Path("vueollama") / "dist"
index_file = dist_dir / "index.html"


@app.get("/get_memo_list")
async def get_memo_list(category: str) -> list[tuple[int, str, str]]:
    """Memoリストを取得.

    Args:
        category (str): カテゴリ

    Returns:
        list[tuple[int, str, str]]: メモのリスト

    """
    db = Db(category)
    memo_list = db.get_memo_list()
    return memo_list  # noqa: RET504


@app.get("/get_memo")
async def get_memo(category: str, memoid: int) -> dict[str, Any]:
    """Memoを取得.

    Args:
        category (str): カテゴリ
        memoid (int): メモID

    Returns:
        dict[str, Any]: 結果

    """
    try:
        db = Db(category)
        memo = db.get_memo(memoid)
    except Exception:  # noqa: BLE001
        msg = traceback.format_exc()
        return {"status": "error", "msg": msg}

    return {"status": "ok", "result": memo}


@app.post("/save_markdown")
async def save_markdown(data: MarkdownDataType) -> dict[str, Any]:
    """Markdownデータを保存.

    Args:
        data (MarkdownDataType): Markdownデータ

    Returns:
        dict[str, Any]: 結果

    """
    try:
        db = Db(data.category)
        db.save_memo(data)
    except Exception:  # noqa: BLE001
        msg = traceback.format_exc()
        return {"status": "error", "msg": msg}

    return {"status": "ok"}


# Catch-all ルートSPA 用の対応
@app.get("/{full_path:path}")
async def serve_spa(full_path: str) -> FileResponse:
    """Vuejs のホスト.

    Args:
        full_path (str): _description_

    Returns:
        FileResponse: _description_

    """
    file_path = dist_dir / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(index_file)


# 静的ファイルをマウント html=True で index.html 自動提供も可
app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
