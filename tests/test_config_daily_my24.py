import unittest
from datetime import datetime, timedelta

from pyspark.sql import SparkSession

from engine_cleaning import apply_statistics_quality_filters
from engine_config import (
    DAILY_MY24_CATALOG,
    get_columns_for_sheet,
    get_default_sheet_ids,
    get_sheet_name_for_context,
)
from engine_loader import get_export_file_name, get_metadata_for_config, get_table_path
from run_local_sample import (
    build_sheet_pivot,
    configure_local_spark_environment,
    get_display_name_for_metric,
    validate_config_columns,
)

SERIES = "DAILY_MY24"
GROUP = "IVECO_DAILY"


class ConfigDailyMy24Test(unittest.TestCase):
    def test_382_384_metadata_and_legacy_routing(self):
        for config in (382, 384):
            self.assertEqual(get_metadata_for_config({config}), ("MISSION_TEST", GROUP, SERIES))
            self.assertEqual(get_table_path(config), f"missiontest.fat_table_{config}")
        self.assertEqual(get_metadata_for_config({382, 384}), ("MISSION_TEST", GROUP, SERIES))
        self.assertEqual(get_export_file_name(GROUP, {382}), "Statistics_DAILY_382_dataset.xlsx")

    def test_catalog_columns_match_template(self):
        self.assertEqual(
            get_columns_for_sheet(SERIES, GROUP, "daily_1b"),
            [f"speed_{low}_{high}" for low, high in
             ((1, 20), (20, 40), (40, 60), (60, 80), (80, 100), (100, 120), (120, 140), (140, 160))],
        )
        self.assertEqual(
            get_columns_for_sheet(SERIES, GROUP, "daily_6b"),
            ["batt_soc_0_60", "batt_soc_60_75", "batt_soc_75_100"],
        )
        self.assertEqual(sum(len(items) for _, items in DAILY_MY24_CATALOG.values()), 89)

    def test_daily_series_ignores_heavy_sheets_and_vice_versa(self):
        self.assertEqual(get_columns_for_sheet(SERIES, GROUP, "1a"), [])
        self.assertEqual(get_columns_for_sheet(SERIES, GROUP, "4h_scr_upstream_temperature"), [])
        self.assertEqual(get_columns_for_sheet("S_WAY_AT_AD_MY_2024", "IVECO_S_WAY", "daily_1a"), [])
        self.assertIn("daily_4e", get_default_sheet_ids())

    def test_sheet_names_fit_excel_limit_and_keep_numbering(self):
        for suffix in DAILY_MY24_CATALOG:
            name = get_sheet_name_for_context(SERIES, GROUP, f"daily_{suffix}")
            self.assertLessEqual(len(name), 31, name)
            self.assertTrue(name.startswith(suffix + ")"), name)

    def test_daily_display_names_do_not_override_heavy_ones(self):
        self.assertEqual(
            get_display_name_for_metric("scr_dwnstr_t_1_daily_4e"),
            "Region 1 SCR Downstream Temperature 400-700 [deg C]",
        )
        self.assertNotIn("400-700", get_display_name_for_metric("scr_dwnstr_t_1") or "")


class DailyQualityFilterAgeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_local_spark_environment()
        cls.spark = (
            SparkSession.builder.master("local[1]")
            .appName("iveco-statistics-daily-tests")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .getOrCreate()
        )

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def _old_dataset(self):
        old = datetime.now() - timedelta(days=700)
        return self.spark.createDataFrame(
            [("V1", old, 5000.0, 100.0, 5.0, 3.0, 2.0)],
            ["vin", "udt_timestamp", "mileage", "enginehours", "speed_1_20", "speed_20_40", "speed_40_60"],
        )

    def test_default_age_limit_drops_old_rows(self):
        self.assertEqual(apply_statistics_quality_filters(self._old_dataset()).count(), 0)

    def test_age_limit_can_be_disabled(self):
        for disabled in (0, None):
            df = apply_statistics_quality_filters(self._old_dataset(), max_data_age_days=disabled)
            self.assertEqual(df.count(), 1)

    def test_daily_sheet_builds_with_disabled_age_limit(self):
        df = apply_statistics_quality_filters(self._old_dataset(), max_data_age_days=0)
        df = df.withColumn("engine_model", df["vin"]).withColumn("mission", df["vin"])
        validation = validate_config_columns(df, SERIES, GROUP, ["daily_1b"])
        df_sheet, sheet_name = build_sheet_pivot(df, "daily_1b", validation["daily_1b"])
        self.assertIsNotNone(df_sheet)
        self.assertFalse(df_sheet.empty)
        self.assertTrue(sheet_name.startswith("1b)"))


if __name__ == "__main__":
    unittest.main()
