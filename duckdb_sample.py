"""DuckDBのサンプル."""

import duckdb


def test01():
    """DuckDB."""
    con = duckdb.connect("ddb.duckdb")
    # テーブルの作成とデータの挿入
    con.execute("CREATE TABLE IF NOT EXISTS  people (name TEXT, age INTEGER)")
    con.execute("INSERT INTO people VALUES ('Alice', 25), ('Bob', 30)")

    # クエリ実行
    df = con.execute("SELECT * FROM people").fetchdf()
    df.to_csv("tmp_test.csv", index=False)
    df.to_parquet("tmp_test.parquet", index=False)
    print(df)

    con.close()


def test02() -> None:
    """DuckDB. read csv pq."""
    # DuckDB 接続の作成
    con = duckdb.connect()

    # CSV を直接読み込んでクエリ実行
    result = con.execute("""
        SELECT *
        FROM read_csv('tmp_test.csv', header=True)
        WHERE age > 25
    """).fetchall()

    print(result)


def test03():
    """DuckDB Parquet."""
    # DuckDB 接続の作成
    con = duckdb.connect()

    # Parquet を直接読み込んでクエリ実行
    result = con.execute("""
        SELECT *
        FROM read_parquet('tmp_test.parquet')
    """).df()

    print(result)


if __name__ == "__main__":
    test03()
