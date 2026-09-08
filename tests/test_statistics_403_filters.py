import json
from datetime import date, timedelta
from pathlib import Path
import unittest

from pyspark.sql import SparkSession

from engine_cleaning import apply_statistics_quality_filters
from engine_config import get_sheet_settings
from run_local_sample import (
    DEFAULT_KEEP_LATEST_PER_VIN,
    MILEAGE_RANGE_ORDER,
    configure_local_spark_environment,
)


class Statistics403QualityFiltersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_local_spark_environment()
        cls.spark = (
            SparkSession.builder.master("local[1]")
            .appName("iveco-statistics-403-tests")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .getOrCreate()
        )

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_quality_filters_keep_only_valid_population_and_null_invalid_metrics(self):
        today = date.today()
        df = self.spark.createDataFrame(
            [
                ("valid", 1001.0, None, 2.0, None, today, None, 2.5, 50.0, 1.0, 1.0),
                ("fuel-zero", 1001.0, None, 2.0, None, today, None, 0.0, 90.0, 1.0, 3.0),
                ("mileage-limit", 1000.0, None, 2.0, None, today, None, 2.5, 50.0, 1.0, 1.0),
                ("old", 1001.0, None, 2.0, None, today - timedelta(days=366), None, 2.5, 50.0, 1.0, 1.0),
                ("legacy", None, 1001.0, None, 2.0, None, today, 2.5, 50.0, 1.0, 1.0),
            ],
            [
                "vin",
                "mileage",
                "cov_div_len",
                "enginehours",
                "tot_eng_hours",
                "udt_timestamp",
                "easy_timestamp",
                "average_fuel_consumption_kml",
                "Average_vehicle_speed",
                "crank_100km",
                "engineoverspeed",
            ],
        )

        result = apply_statistics_quality_filters(df).orderBy("vin").collect()

        self.assertEqual([row.vin for row in result], ["fuel-zero", "legacy", "valid"])
        by_vin = {row.vin: row for row in result}
        self.assertIsNone(by_vin["fuel-zero"].average_fuel_consumption_kml)
        self.assertIsNone(by_vin["fuel-zero"].Average_vehicle_speed)
        self.assertIsNone(by_vin["fuel-zero"].engineoverspeed_pct)
        self.assertEqual(by_vin["valid"].engineoverspeed_pct, 50.0)
        self.assertEqual(by_vin["valid"].crank_100km_pct, 50.0)
        self.assertEqual(by_vin["legacy"].mileage, 1001.0)
        self.assertEqual(by_vin["legacy"].enginehours, 2.0)


class Statistics403ConfigurationTest(unittest.TestCase):
    def test_average_vehicle_speed_uses_speed_bands_not_mileage_bands(self):
        self.assertEqual(
            get_sheet_settings("average_vehicle_speed")["group_by"],
            ["Average_vehicle_speed_split"],
        )

    def test_mileage_labels_use_millions_not_ambiguous_1000k(self):
        self.assertIn("900k-1M km", MILEAGE_RANGE_ORDER)
        self.assertIn(">1M km", MILEAGE_RANGE_ORDER)
        self.assertFalse(any("1000k" in label for label in MILEAGE_RANGE_ORDER))

    def test_latest_vin_is_default_in_runner_and_notebook(self):
        self.assertTrue(DEFAULT_KEEP_LATEST_PER_VIN)

        notebook_path = Path(__file__).parents[1] / "Main_pipeline_modular.ipynb"
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        source = "".join(notebook["cells"][2]["source"])

        self.assertIn('DEFAULT_KEEP_LATEST_PER_VIN = True', source)
        self.assertIn('dropdown("keep_latest_per_vin", "Yes", ["Yes", "No"]', source)


if __name__ == "__main__":
    unittest.main()
