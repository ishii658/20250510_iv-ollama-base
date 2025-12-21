"""FastAPI + IonicVue の SPA 配信サーバー."""

import traceback
from pathlib import Path
from typing import Any

from fastapi import FastAPI

# from fastapi.responses import FileResponse  # noqa: ERA001
from fastapi.staticfiles import StaticFiles

from db import Db, MarkdownDataType

app = FastAPI()

# dist ディレクトリ
dist_dir = Path("vueollama") / "dist"


# -----------------------------
# API は /api 以下に集約
# -----------------------------
@app.get("/api/get_memo_list")
async def get_memo_list(category: str) -> list[tuple[int, str, str]]:
    """メモリストを取得.

    Args:
        category (str): _description_

    Returns:
        list[tuple[int, str, str]]: _description_

    """
    db = Db(category)
    memo_list = db.get_memo_list()
    return memo_list  # noqa: RET504


@app.get("/api/get_memo")
async def get_memo(category: str, memoid: int) -> dict[str, Any]:
    """メモを取得.

    Args:
        category (str): _description_
        memoid (int): _description_

    Returns:
        dict[str, Any]: _description_

    """
    try:
        db = Db(category)
        memo = db.get_memo(memoid)
        return {"status": "ok", "result": memo}  # noqa: TRY300
    except Exception:  # noqa: BLE001
        return {"status": "error", "msg": traceback.format_exc()}


@app.post("/api/save_markdown")
async def save_markdown(data: MarkdownDataType) -> dict[str, Any]:
    """やり取りの結果を保存.

    Args:
        data (MarkdownDataType): _description_

    Returns:
        dict[str, Any]: _description_

    """
    try:
        db = Db(data.category)
        db.save_memo(data)
        return {"status": "ok"}  # noqa: TRY300
    except Exception:  # noqa: BLE001
        return {"status": "error", "msg": traceback.format_exc()}


@app.get("/api/del_markdown")
async def del_markdown(category: str, memoid: int) -> dict[str, Any]:
    """保存した履歴を削除.

    Args:
        category (str): _description_
        memoid (int): _description_

    Returns:
        dict[str, Any]: _description_

    """
    try:
        db = Db(category)
        db.del_memo(memoid)
        return {"status": "ok"}  # noqa: TRY300
    except Exception:  # noqa: BLE001
        return {"status": "error", "msg": traceback.format_exc()}


# -----------------------------
# 静的ファイル (Ionic Vue SPA)
# -----------------------------
# html=True → index.html を自動返却（Catch-all 不要）  # noqa: RUF003
app.mount("/", StaticFiles(directory=dist_dir, html=True), name="spa")
