from run_local_sample import copy_excel_to_dbfs


class FakeFs:
    def __init__(self):
        self.mkdirs_calls = []
        self.cp_calls = []

    def mkdirs(self, path):
        self.mkdirs_calls.append(path)

    def cp(self, source, target, recurse):
        self.cp_calls.append((source, target, recurse))


class FakeDbutils:
    def __init__(self):
        self.fs = FakeFs()


class FakeConf:
    def get(self, key, default=None):
        if key == "spark.databricks.workspaceUrl":
            return "adb.example.azuredatabricks.net"
        return default


class FakeSpark:
    conf = FakeConf()


def test_copy_excel_to_dbfs_uses_generated_file_name(tmp_path):
    excel_path = tmp_path / "Statistics_HEAVY_XWAY_408_dataset.xlsx"
    excel_path.write_bytes(b"excel")
    dbutils = FakeDbutils()

    result = copy_excel_to_dbfs(excel_path, dbutils, spark=FakeSpark())

    assert dbutils.fs.mkdirs_calls == ["dbfs:/FileStore/iveco_statistics_output"]
    assert dbutils.fs.cp_calls == [
        (
            f"file:{excel_path.resolve().as_posix()}",
            "dbfs:/FileStore/iveco_statistics_output/Statistics_HEAVY_XWAY_408_dataset.xlsx",
            True,
        )
    ]
    assert result["dbfs_path"].endswith("/Statistics_HEAVY_XWAY_408_dataset.xlsx")
    assert result["download_url"].endswith(
        "/files/iveco_statistics_output/Statistics_HEAVY_XWAY_408_dataset.xlsx"
    )


def test_copy_excel_to_dbfs_rejects_missing_file(tmp_path):
    dbutils = FakeDbutils()
    missing = tmp_path / "missing.xlsx"

    try:
        copy_excel_to_dbfs(missing, dbutils)
    except FileNotFoundError as exc:
        assert "Excel non trovato" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")
