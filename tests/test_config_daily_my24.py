import unittest
from datetime import datetime, timedelta

from pyspark.sql import SparkSession

from engine_cleaning import add_legacy_preparation_features, apply_statistics_quality_filters
from engine_config import (
    DAILY_MISSION_LABELS,
    DAILY_MY24_CATALOG,
    get_columns_for_sheet,
    get_default_sheet_ids,
    get_sheet_name_for_context,
)
from engine_loader import (
    get_export_file_name,
    get_metadata_for_config,
    get_quality_filter_overrides,
    get_table_path,
)
from run_local_sample import (
    build_sheet_pivot,
    export_excel_outputs,
    configure_local_spark_environment,
    get_display_name_for_metric,
    validate_config_columns,
)

SERIES = "DAILY_MY24"
GROUP = "IVECO_DAILY"


class ConfigDailyMy24Test(unittest.TestCase):
    def test_382_384_metadata_and_unity_catalog_routing(self):
        for config in (382, 384):
            self.assertEqual(get_metadata_for_config({config}), ("MISSION_TEST", GROUP, SERIES))
            self.assertEqual(
                get_table_path(config),
                f"u_truck_analyzer_p.mission_test_statistics.fat_table_{config}",
            )
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
        # Default = solo il report LIGHT; il catalogo completo resta opt-in.
        self.assertEqual(
            [sid for sid in get_default_sheet_ids() if sid.startswith("daily_")],
            [
                "daily_fuel_kml_2",
                "daily_light_1a_f1a",
                "daily_light_1a_f1c",
                "daily_light_1c_f1a",
                "daily_light_1c_f1c",
                "daily_light_6a",
                "daily_light_6b",
            ],
        )
        self.assertNotIn("daily_4e", get_default_sheet_ids())

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

    def test_quality_range_override_only_for_daily_configs(self):
        self.assertEqual(get_quality_filter_overrides({382, 384}), {"average_fuel_consumption_kml": (0.1, 25.0)})
        self.assertEqual(get_quality_filter_overrides({399}), {})
        self.assertEqual(get_quality_filter_overrides({382, 399}), {})

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


    def test_engine_model_is_derived_from_engine_type_when_product_model_is_unhelpful(self):
        df = self.spark.createDataFrame(
            [("V1", "DAILY 35S", "F1AGL411A", None), ("V2", None, "xx F1CE3481 yy", "C13"), ("V3", None, None, None)],
            "vin string, product_model string, engine_type string, engine_code string",
        )
        df = add_legacy_preparation_features(df)
        engines = {row["vin"]: row["engine_model"] for row in df.select("vin", "engine_model").collect()}
        self.assertEqual(engines, {"V1": "F1A", "V2": "F1C", "V3": "Unknown"})

    def test_light_report_matches_past_example_layout(self):
        import tempfile
        import pandas as pd

        old = datetime.now() - timedelta(days=30)
        rows = []
        for i in range(6):
            engine, power = ("F1A", "136 EVI") if i % 2 == 0 else ("F1C", "160 EVI")
            rows.append((
                f"V{i}", old, 20000.0 if i % 3 else 5000.0, 100.0, engine, power,
                "Cab 35C Daily 4x2 MY2024 (F35C)", "3.15", [10.0, 20.0, 30.0, 60.0, 12.0, 22.0][i], 13.0 - i,
                50.0 + i, 30.0, 20.0, 10.0, 5.0, 3.0, 2.0,
                40.0, 30.0, 20.0, 10.0,
                1.0, 9.0, 90.0, 30.0, 20.0, 50.0,
            ))
        columns = [
            "vin", "udt_timestamp", "mileage", "enginehours", "engine_model", "power",
            "product_model", "axle_description", "Average_vehicle_speed", "average_fuel_consumption_kml",
            "rev_tor_idle", "rev_tor_cutoff", "rev_tor_extrlow", "rev_tor_low",
            "rev_tor_opt", "rev_tor_tor", "rev_tor_high",
            "torque_15_30", "torque_30_60", "torque_60_90", "torque_90_110",
            "batt_volt_7_11", "batt_volt_11_12", "batt_volt_12_15",
            "batt_soc_0_60", "batt_soc_60_75", "batt_soc_75_100",
        ]
        df = self.spark.createDataFrame(rows, columns)
        df = apply_statistics_quality_filters(
            df, metric_range_overrides=get_quality_filter_overrides({382})
        )
        df = add_legacy_preparation_features(df)
        sheet_ids = [sid for sid in get_default_sheet_ids() if sid.startswith("daily_")]
        validation = validate_config_columns(df, SERIES, GROUP, sheet_ids)
        outputs = []
        for sid in sheet_ids:
            df_sheet, sheet_name = build_sheet_pivot(df, sid, validation[sid])
            self.assertIsNotNone(df_sheet, sid)
            outputs.append({"sheet_id": sid, "sheet_name": sheet_name, "dataframe": df_sheet})
        with tempfile.TemporaryDirectory() as tmp:
            path = export_excel_outputs(outputs, tmp, "daily.xlsx")
            book = pd.read_excel(path, sheet_name=None)
        self.assertEqual(
            list(book),
            ["Fuel Consumption km_l 2", "Engine Speed vs Torque F1A", "Engine Speed vs Torque F1C", "Engine Torque F1A",
             "Engine Torque F1C", "Battery Voltage", "Battery SOC"],
        )
        fuel = book["Fuel Consumption km_l 2"]
        self.assertEqual(
            list(fuel.columns[:6]),
            ["Engine Model", "Product Model", "Power", "Axle Description", "Mission",
             "Average fuel consumption [km/l]"],
        )
        self.assertEqual(fuel.columns[-1], "Count")
        self.assertTrue(set(fuel["Mission"]) <= set(DAILY_MISSION_LABELS))
        self.assertIn("15 – 25 km/h URBAN", set(fuel["Mission"]))
        self.assertGreater(fuel["Average fuel consumption [km/l]"].astype(float).max(), 6.0)

        speed_a = book["Engine Speed vs Torque F1A"]
        self.assertEqual(list(speed_a.columns[:3]), ["Engine Model", "Power", "Rev Tor Idle"])
        self.assertEqual(list(speed_a.columns[3:6]), ["Standard Deviation", "Advice", "Alert"])
        self.assertEqual(speed_a.columns[-1], "Count")
        self.assertEqual(set(speed_a["Engine Model"]), {"F1A"})
        self.assertEqual(set(book["Engine Torque F1C"]["Engine Model"]), {"F1C"})
        self.assertIn("Torque 15 30", book["Engine Torque F1A"].columns)
        voltage = book["Battery Voltage"]
        self.assertEqual(voltage.columns[0], "Mileage Split")
        self.assertIn("Critical Voltage region  7-11 [Volt]", voltage.columns)
        self.assertEqual(list(voltage["Mileage Split"]), ["<10k km", "over 10k km"])


if __name__ == "__main__":
    unittest.main()
