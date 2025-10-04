"""データベース Read,Write."""

import sqlite3
from typing import Any

from pydantic import BaseModel

"""
,------------------.
|memo              |
|------------------|
|*id : int <<PK>>  |
|--                |
|title : text      |
|description : text|
`------------------'
          |
memo.id = memo_md.memoid
          |
 ,----------------. 
 |memo_md         | 
 |----------------| 
 |*id : int <<PK>>| 
 |--              | 
 |memoid : int    | 
 |model : text    | 
 |msg : text      | 
 `----------------' 
"""


class MarkdownMessageType(BaseModel):
    """MarkdownDataType.md_list."""

    model: str
    msg: str = ""


class MarkdownDataType(BaseModel):
    """Markdown保存Postデータ."""

    category: str = "memo"
    """カテゴリ"""

    title: str = ""
    """タイトル"""

    description: str = ""
    """説明"""

    md_list: list[MarkdownMessageType]
    """Markdown 文字列とuser,think,回答モデルの区別"""


g_create_memo_table = """
CREATE TABLE IF NOT EXISTS memo (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT
);
"""

# SQLiteはデフォルトで外部キー制約が無効なので、使う前に必ず
# PRAGMA foreign_keys = ON;
# conn.execute("PRAGMA foreign_keys = ON;")  # noqa: ERA001
g_create_memo_md_table = """
CREATE TABLE IF NOT EXISTS memo_md (
    id INTEGER PRIMARY KEY,
    memoid INTEGER,
    model TEXT,
    msg TEXT,
    FOREIGN KEY (memoid) REFERENCES memo(id) ON DELETE CASCADE
)
"""


class Db:
    """DB読み書き用のクラス."""

    def __init__(self, category: str = "memo") -> None:
        """コンストラクタ. カテゴリーを設定.

        Args:
            category (str, optional): _description_. Defaults to "memo".

        """
        self.category = category

    def get_memo_list(self) -> list[tuple[int, str, str]]:
        """Id, title, description のリストを取得するメソッド.

        Returns:
            list[tuple[int, str, str]]: id, title, descriptionのリスト

        """
        # ここでは仮にSQL発行するとして例示
        # 実際は self.category に応じてDB接続等で切り替えなど
        # 例: SQLite3, SQLAlchemy, asyncpg など環境に合わせて書き換え

        # --- 例 (SQLite3) ---
        import sqlite3

        conn = sqlite3.connect(f"{self.category}.sqlite3")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM memo")
        rows: list[tuple[int, str, str]] = cursor.fetchall()
        conn.close()

        result: list[tuple[int, str, str]] = []
        for row in rows:
            memo = (row[0], row[1], row[2])
            result.append(memo)
        return result

    def get_memo(self, memoid: int) -> list[tuple[str, str]]:
        """Memoを取得.

        Args:
            memoid (int): memo id

        Returns:
            list[tuple[str, str]]: 結果

        """
        con = sqlite3.connect(f"{self.category}.sqlite3")
        cur = con.cursor()
        try:
            # パラメータを使って安全にクエリを実行
            cur.execute("SELECT model, msg FROM memo_md WHERE memoid = ?", (memoid,))

            # 結果を取得
            results: list[tuple[str, str]] = cur.fetchall()
        except Exception as e:
            msg = "get_memo"
            raise Exception(msg) from e  # noqa: TRY002
        finally:
            cur.close()
            con.close()
        return results

    def _save_memo(self, title: str, description: str) -> int:
        """Memoテーブルにmemoを保存して登録したidを返す.

        Args:
            title (str): タイトル
            description (str): 説明

        Returns:
            int: 登録id

        """
        con = sqlite3.connect(f"{self.category}.sqlite3")
        con.execute("PRAGMA foreign_keys = ON;")
        cur = con.cursor()
        try:
            # create table
            cur.execute(g_create_memo_table)
            # insert
            sql = "INSERT INTO memo (title, description) VALUES (?, ?)"
            cur.execute(sql, (title, description))
            lastid = cur.lastrowid

        except sqlite3.DatabaseError as e:
            con.rollback()
            raise sqlite3.DatabaseError from e
        except Exception as e:
            con.rollback()
            raise Exception from e  # noqa: TRY002
        finally:
            con.commit()
            cur.close()
            con.close()

        return lastid

    def _save_markdown(self, memoid: int, data: MarkdownDataType) -> None:
        """テーブルに Markdown を保存.

        Args:
            memoid (int): memoid
            data (MarkdownDataType): Markdown のリストを収めたデータ

        Raises:
            sqlite3.DatabaseError: データベースエラー
            Exception: その他の例外

        """
        # 書き込みデータを準備 [(memo_id, model, msg)]  # noqa: ERA001
        wt_data: list[tuple[int, str, str]] = []
        for row in data.md_list:
            a_data = (memoid, row.model, row.msg)
            wt_data.append(a_data)

        con = sqlite3.connect(f"{self.category}.sqlite3")
        con.execute("PRAGMA foreign_keys = ON;")
        cur = con.cursor()
        try:
            # create table
            cur.execute(g_create_memo_md_table)
            # insert
            sql = "INSERT INTO memo_md (memoid, model, msg) VALUES (?, ?, ?)"
            cur.executemany(sql, wt_data)
            con.commit()
        except sqlite3.DatabaseError as e:
            con.rollback()
            raise sqlite3.DatabaseError from e
        except Exception as e:
            con.rollback()
            raise Exception from e  # noqa: TRY002
        finally:
            cur.close()
            con.close()

    def save_memo(self, md_data: MarkdownDataType) -> None:
        """MMarkdown データを保存.

        Args:
            md_data (MarkdownDataType): 保存するデータ
            title (str): タイトル
            description (str): 説明

        """
        # memo を保存
        memoid = self._save_memo(md_data.title, md_data.description)

        # memoの中身を保存
        self._save_markdown(memoid, md_data)

    def del_memo(self, md_id: int) -> None:
        """メモを削除.

        Args:
            md_id (int): memo id
            category (str): カテゴリ

        """
        con = sqlite3.connect(f"{self.category}.sqlite3")
        con.execute("PRAGMA foreign_keys = ON;")
        cur = con.cursor()
        try:
            # memo テーブルから id = 1 のデータを削除
            con.execute("DELETE FROM memo WHERE id = ?", (md_id,))
            con.commit()
        except sqlite3.DatabaseError as e:
            con.rollback()
            raise sqlite3.DatabaseError from e
        except Exception as e:
            con.rollback()
            raise Exception from e  # noqa: TRY002
        finally:
            cur.close()
            con.close()
