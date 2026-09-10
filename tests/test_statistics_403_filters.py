import json
from datetime import date, datetime, timedelta
from pathlib import Path
import unittest

import pandas as pd
from pyspark.sql import SparkSession

from engine_cleaning import (
    add_np_403_calculated_features,
    apply_statistics_quality_filters,
    exclude_corrupt_statistics_rows,
    keep_latest_record_per_vin,
)
from engine_config import get_sheet_settings
from run_local_sample import (
    DEFAULT_KEEP_LATEST_PER_VIN,
    MILEAGE_RANGE_ORDER,
    build_sheet_pivot,
    build_sheet_outputs,
    configure_local_spark_environment,
    format_seconds_as_hhmmss,
    validate_config_columns,
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

    def test_np_timer_columns_are_normalized_from_clock_and_numeric_values(self):
        df = self.spark.createDataFrame(
            [
                (
                    "12.5",
                    250000.0,
                    "01:02:03",
                    "00:02:00",
                    "00:03:00",
                    "25:00:00",
                    "30",
                    "00:10:00",
                    "00:20:00",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                )
            ],
            [
                "Engine_on_time",
                "mileage",
                "Engine_overspeed_2600_rpm_Timer",
                "Post_Catalyst_temperature_860_timer",
                "Cat_Eff_Timer",
                "Coolant_temperature_high_104_timer",
                "High_oil_temperature_120_timer",
                "High_boost_pressure_timer",
                "Low_ambient_pressure_timer",
                "Cat_Eff_Counter",
                "Coolant_temperature_high_104_counter",
                "High_oil_temperature_120_counter",
                "High_boost_pressure_counter",
                "Low_ambient_pressure_counter",
            ],
        )

        row = add_np_403_calculated_features(df).first()

        self.assertEqual(row.Engine_on_time, 12.5)
        self.assertEqual(row.engine_life_cycle, 75.0)
        self.assertEqual(row.engineoverspeed, 3723.0)
        self.assertEqual(row.Catalyst_temp_860, 2.0)
        self.assertEqual(row.Low_Cat_Eff_time, 3.0)
        self.assertEqual(row.Low_Cat_Eff_count, 4.0)
        self.assertEqual(row.Coolant_temp_high_104, 90000.0)
        self.assertEqual(row.Oil_temp_high_120, 30.0)
        self.assertEqual(row.Boost_pressure_high_25, 10.0)
        self.assertEqual(row.Ambient_pressure_low_850, 1200.0)
        self.assertEqual(row.High_boost_pressure_counter, 7.0)

    def test_np_final_calculated_values_take_priority_over_raw_timers(self):
        df = self.spark.createDataFrame(
            [(5.0, "00:10:00", 2.0, "9")],
            ["Boost_pressure_high_25", "High_boost_pressure_timer", "Low_Cat_Eff_count", "Cat_Eff_Counter"],
        )

        row = add_np_403_calculated_features(df).first()

        self.assertEqual(row.Boost_pressure_high_25, 5.0)
        self.assertEqual(row.Low_Cat_Eff_count, 2.0)

    def test_np_vehicle_speed_excludes_over_40_and_adds_missing_under_20_band(self):
        df = self.spark.createDataFrame(
            [
                ("20-40 km/h", 30.0),
                (">40 km/h", 50.0),
            ],
            ["Average_vehicle_speed_split", "Average_vehicle_speed"],
        )
        validation = {
            "present": ["Average_vehicle_speed"],
            "sheet_name": "Average Vehicle Speed",
        }

        result, _ = build_sheet_pivot(df, "np_average_vehicle_speed", validation)

        self.assertEqual(set(result["Average_vehicle_speed_split"]), {"<20 km/h", "20-40 km/h"})
        under_20 = result[result["Average_vehicle_speed_split"] == "<20 km/h"].iloc[0]
        self.assertTrue(pd.isna(under_20["Average_vehicle_speed"]))
        self.assertEqual(under_20["Count_Average_vehicle_speed"], 0)

    def test_corrupt_latest_np_403_record_falls_back_to_previous_valid_record(self):
        df = self.spark.createDataFrame(
            [
                (
                    "ZCFEG2RP70C542992",
                    403,
                    datetime(2026, 8, 1),
                    45.0,
                    1200.0,
                    2.0,
                    5.0,
                    2000.0,
                ),
                (
                    "ZCFEG2RP70C542992",
                    403,
                    datetime(2026, 9, 1),
                    538976248.0,
                    8982946.67,
                    167471.52,
                    538976288.0,
                    1792.05,
                ),
            ],
            [
                "vin",
                "id_config",
                "udt_timestamp",
                "Average_vehicle_speed",
                "Average_enginespeed",
                "avgcrank_100km",
                "engineoverspeed",
                "enginehours",
            ],
        )

        row = keep_latest_record_per_vin(df).first()

        self.assertEqual(row.udt_timestamp, datetime(2026, 8, 1))
        self.assertEqual(row.Average_vehicle_speed, 45.0)

    def test_single_bad_metric_does_not_remove_np_403_record(self):
        df = self.spark.createDataFrame(
            [("single-error", 403, 90.0, 1200.0, 2.0, 5.0, 2000.0)],
            [
                "vin",
                "id_config",
                "Average_vehicle_speed",
                "Average_enginespeed",
                "avgcrank_100km",
                "engineoverspeed",
                "enginehours",
            ],
        )

        self.assertEqual(exclude_corrupt_statistics_rows(df).count(), 1)

    def test_fuel_sheet_leaves_statistics_blank_when_all_values_are_zero(self):
        df = self.spark.createDataFrame(
            [("NP", "340C9G", "5.29", ">50 km/h HIGHWAY", 0.0)],
            ["product_model", "power", "axle_description", "mission", "average_fuel_consumption_kml"],
        )
        validation = {
            "present": ["average_fuel_consumption_kml"],
            "sheet_name": "Fuel Consumption",
        }

        result, _ = build_sheet_pivot(df, "fuel_consumption", validation)
        row = result.iloc[0]

        self.assertTrue(pd.isna(row["average_fuel_consumption_kml"]))
        self.assertTrue(pd.isna(row["StdDev_average_fuel_consumption_kml"]))
        self.assertTrue(pd.isna(row["Advice_average_fuel_consumption_kml"]))
        self.assertTrue(pd.isna(row["Alert_average_fuel_consumption_kml"]))
        self.assertEqual(row["Count_average_fuel_consumption_kml"], 0)

    def test_duration_formatter_keeps_hours_above_24(self):
        self.assertEqual(format_seconds_as_hhmmss(90061), "25:01:01")

    def test_np_profile_builds_every_requested_sheet(self):
        sheet_ids = [
            "fuel_consumption",
            "np_average_vehicle_speed",
            "np_engine_lifecycle",
            "np_engine_overspeed",
            "np_catalyst_temperature",
            "np_low_catalyst_efficiency",
            "np_coolant_temperature_high",
            "np_oil_temperature_high",
            "np_boost_pressure_high",
            "np_ambient_pressure_low",
            "np_2a",
            "np_2b",
            "np_2c",
            "np_3a",
            "np_3c",
            "np_3f",
            "np_3g",
            "np_4d",
            "np_5c",
        ]
        values = {
            "product_model": "C S-Way NP",
            "power": "340C9G",
            "axle_description": "5.29",
            "mission": "20 - 40 km/h URBAN",
            "engine_model": "Cursor 9",
            "mileage": 250000.0,
            "mileage_range": "200k-300k km",
            "Average_vehicle_speed_split": "20-40 km/h",
            "Average_vehicle_speed": 30.0,
            "average_fuel_consumption_kml": 0.0,
            "engine_life_cycle": 75.0,
            "engineoverspeed": 30.0,
            "Catalyst_temp_860": 0.0,
            "Low_Cat_Eff_time": 0.0,
            "Low_Cat_Eff_count": 0.0,
            "Coolant_temp_high_104": 240.0,
            "Oil_temp_high_120": 0.0,
            "Boost_pressure_high_25": 6.0,
            "Ambient_pressure_low_850": 0.0,
        }
        for column_name in (
            "region1_coolantT", "region2_coolantT",
            "oiltemp1", "oiltemp2", "oiltemp3",
            "reg1_Intake_Temp", "reg2_Intake_Temp", "reg3_Intake_Temp",
            "fueltemp1", "fueltemp2", "fueltemp3",
            "reg1_gas_railpressure", "reg2_gas_railpressure", "reg3_gas_railpressure",
            "reg1_Mixture_selfpoor", "reg2_Mixture_selfpoor", "reg3_Mixture_selfpoor",
            "reg1_Mixture_selfrich", "reg2_Mixture_selfrich", "reg3_Mixture_selfrich",
            "reg1_Cat_Eff", "reg2_Cat_Eff", "reg3_Cat_Eff",
            "reg1_Intake_manifoldpressure", "reg2_Intake_manifoldpressure",
            "reg3_Intake_manifoldpressure",
        ):
            values[column_name] = 1.0

        df = self.spark.createDataFrame([tuple(values.values())], list(values))
        df = add_np_403_calculated_features(df)
        validation = validate_config_columns(
            df,
            "S_WAY_NP_MY_2024",
            "IVECO_S_X_WAY_NP",
            sheet_ids,
        )

        outputs = build_sheet_outputs(df, validation)

        self.assertEqual({output["sheet_id"] for output in outputs}, set(sheet_ids))
        coolant = next(
            output["dataframe"]
            for output in outputs
            if output["sheet_id"] == "np_coolant_temperature_high"
        )
        self.assertEqual(coolant.iloc[0]["Coolant_temp_high_104"], 240.0)


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
