import unittest

from engine_config import (
    get_columns_for_sheet,
    get_default_sheet_ids,
    get_sheet_name_for_context,
    get_sheet_settings,
    is_new_layout_series,
)
from engine_loader import get_export_file_name, get_metadata_for_config, get_table_path
from run_local_sample import MILEAGE_RANGE_ORDER, MISSION_ORDER, prepare_excel_dataframe

import pandas as pd


class Config405406Test(unittest.TestCase):
    def test_new_configs_use_unity_catalog_mission_test_tables(self):
        for config in (403, 405, 406, 408):
            self.assertEqual(
                get_table_path(config),
                f"u_truck_analyzer_p.mission_test_statistics.fat_table_{config}",
            )

    def test_known_fat_table_configs_use_static_metadata(self):
        self.assertEqual(
            get_metadata_for_config({403}),
            ("MISSION_TEST", "IVECO_S_X_WAY_NP", "S_WAY_NP_MY_2024"),
        )
        self.assertEqual(
            get_metadata_for_config({399}),
            ("MISSION_TEST", "IVECO_S_WAY", "S_WAY_AT_AD_MY_2024"),
        )
        self.assertEqual(
            get_metadata_for_config({405}),
            ("MISSION_TEST", "IVECO_X_WAY", "X_WAY_AT_AD_MY_2024"),
        )
        self.assertEqual(
            get_metadata_for_config({406}),
            ("MISSION_TEST", "IVECO_T_WAY", "T_WAY_MY_2024"),
        )
        self.assertEqual(
            get_metadata_for_config({408}),
            ("MISSION_TEST", "IVECO_X_WAY", "X_WAY_AT_AD_MY_2024"),
        )

    def test_my24_series_variants_use_new_layout_columns(self):
        self.assertTrue(is_new_layout_series("X-WAY MY24 AT/AD_V1.6.4 C9"))
        self.assertTrue(is_new_layout_series("T-WAY_MY_2024"))
        self.assertEqual(
            get_columns_for_sheet("X-WAY MY24 AT/AD_V1.6.4 C9", "IVECO_X-WAY", "1a"),
            [
                "tor_rev_cutoff",
                "tor_rev_low",
                "tor_rev_lowlow",
                "tor_rev_high_1",
                "tor_rev_opt",
                "tor_rev_highlow",
                "tor_rev_high_2",
            ],
        )

    def test_export_file_name_handles_hyphenated_groups(self):
        self.assertEqual(
            get_export_file_name("IVECO_S_X_WAY_NP", {403}),
            "Statistics_HEAVY_SWAY_NP_403_dataset.xlsx",
        )
        self.assertEqual(
            get_export_file_name("IVECO_X-WAY", {405}),
            "Statistics_HEAVY_XWAY_405_dataset.xlsx",
        )
        self.assertEqual(
            get_export_file_name("IVECO_T-WAY", {406}),
            "Statistics_HEAVY_TWAY_406_dataset.xlsx",
        )
        self.assertEqual(
            get_export_file_name("IVECO_X-WAY", {408}),
            "Statistics_HEAVY_XWAY_408_dataset.xlsx",
        )

    def test_config_399_uses_specific_oil_pressure_variables(self):
        self.assertEqual(
            get_columns_for_sheet("S_WAY_AT_AD_MY_2024", "IVECO_S_WAY", "2a"),
            ["p_oil_1", "p_oil_2", "p_oil_3"],
        )

    def test_excel_export_names_sorts_categories_and_moves_counts_to_end(self):
        df = pd.DataFrame(
            {
                "engine_model": ["Cursor 9"] * 4,
                "mission": [
                    "20 - 40 km/h URBAN",
                    "40 - 50 km/h MIX URBAN/ MEDIUM HIGHWAY",
                    "<20 km/h HEAVY URBAN",
                    ">50 km/h HIGHWAY",
                ],
                "TOR_REV_CUTOFF_1A": [1, 2, 3, 4],
                "StdDev_TOR_REV_CUTOFF_1A": [0, 0, 0, 0],
                "Advice_TOR_REV_CUTOFF_1A": [1, 2, 3, 4],
                "Alert_TOR_REV_CUTOFF_1A": [1, 2, 3, 4],
                "Count_TOR_REV_CUTOFF_1A": [10, 20, 30, 40],
                "TOR_REV_LOW_1A": [5, 6, 7, 8],
                "StdDev_TOR_REV_LOW_1A": [0, 0, 0, 0],
                "Advice_TOR_REV_LOW_1A": [5, 6, 7, 8],
                "Alert_TOR_REV_LOW_1A": [5, 6, 7, 8],
                "Count_TOR_REV_LOW_1A": [10, 20, 30, 40],
            }
        )

        exported = prepare_excel_dataframe(df)

        self.assertEqual(exported["mission"].tolist(), MISSION_ORDER)
        self.assertIn(
            "Cut off with gear engaged (250-2500 rpm / -15 - 0 %)",
            exported.columns,
        )
        self.assertIn("Low Load (250-2500 rpm / 0-15%)", exported.columns)
        self.assertEqual(exported.columns[-1], "count")
        self.assertEqual(list(exported.columns).count("count"), 1)

    def test_excel_export_sorts_mileage_and_mission_with_multiple_group_columns(self):
        df = pd.DataFrame(
            {
                "engine_model": ["Cursor 9"] * 5,
                "power": ["340 C9"] * 5,
                "mileage_range": [
                    "10k-100k km",
                    "10k-100k km",
                    "<10k km",
                    "<10k km",
                    "10k-100k km",
                ],
                "mission": [
                    "20 - 40 km/h URBAN",
                    "<20 km/h HEAVY URBAN",
                    "20 - 40 km/h URBAN",
                    "<20 km/h HEAVY URBAN",
                    "40 - 50 km/h MIX URBAN/ MEDIUM HIGHWAY",
                ],
                "CAT_EFF_SCR_2_A_4A": [1, 2, 3, 4, 5],
            }
        )

        exported = prepare_excel_dataframe(df)

        self.assertEqual(
            exported["mileage range"].tolist(),
            ["<10k km", "<10k km", "10k-100k km", "10k-100k km", "10k-100k km"],
        )
        self.assertEqual(
            exported["mission"].tolist(),
            [
                "<20 km/h HEAVY URBAN",
                "20 - 40 km/h URBAN",
                "<20 km/h HEAVY URBAN",
                "20 - 40 km/h URBAN",
                "40 - 50 km/h MIX URBAN/ MEDIUM HIGHWAY",
            ],
        )
        self.assertEqual(exported["mileage range"].iloc[0], MILEAGE_RANGE_ORDER[0])

    def test_customer_notes_update_sheets_4e_4f_temperature_and_5c(self):
        self.assertEqual(get_sheet_settings("4e")["name"], "4e) Urea deposit accumulation")
        self.assertEqual(get_sheet_settings("4e")["group_by"], ["engine_model", "mission"])
        self.assertEqual(
            get_columns_for_sheet("X-WAY MY24 AT/AD_V1.6.4 C9", "IVECO_X-WAY", "4e"),
            ["urea_dep_1", "urea_dep_2", "urea_dep_3", "urea_dep_4"],
        )
        self.assertEqual(get_sheet_settings("4f")["name"], "4f) AdBlue pressure pump")
        self.assertEqual(
            get_columns_for_sheet("X-WAY MY24 AT/AD_V1.6.4 C9", "IVECO_X-WAY", "4f"),
            ["urea_p_1", "urea_p_2", "urea_p_3", "urea_p_4"],
        )

        for sheet_id in (
            "4g_doc_upstream_temperature",
            "4h_scr_upstream_temperature",
            "4i_scr_downstream_temperature",
        ):
            settings = get_sheet_settings(sheet_id)
            self.assertTrue(settings["use_percentage_columns"])
            self.assertFalse(settings["zero_as_null"])

        self.assertEqual(get_sheet_settings("5c")["trigger"], 0)

    def test_turbocharger_130000_keeps_zero_values(self):
        settings = get_sheet_settings("turbocharger_revolutions")

        self.assertTrue(settings["zero_as_null"])
        self.assertEqual(settings["zero_as_null_exclude"], ["Turbochargerrevolutions_130000"])

    def test_403_uses_timer_overspeed_and_normalized_crank_metrics(self):
        self.assertEqual(
            get_columns_for_sheet("S_WAY_NP_MY_2024", "IVECO_S_X_WAY_NP", "engine_over_speed"),
            [],
        )
        self.assertEqual(
            get_columns_for_sheet("S_WAY_NP_MY_2024", "IVECO_S_X_WAY_NP", "np_engine_overspeed"),
            ["engineoverspeed"],
        )
        for sheet_id in ("average_crank_per_100km", "average_crank_per_100km_2"):
            settings = get_sheet_settings(sheet_id)
            self.assertEqual(
                get_columns_for_sheet("S_WAY_NP_MY_2024", "IVECO_S_X_WAY_NP", sheet_id),
                ["crank_100km_pct"],
            )
            self.assertEqual(settings["scale"], 1)

    def test_403_np_uses_dedicated_sheets_and_excludes_diesel_collisions(self):
        series = "S_WAY_NP_MY_2024"
        group = "IVECO_S_X_WAY_NP"

        for sheet_id in ("1a", "1a_2", "1b", "2a", "2b", "2c", "3a", "3c", "3f", "4d", "5c"):
            self.assertEqual(get_columns_for_sheet(series, group, sheet_id), [])

        expected = {
            "np_2a": ["region1_coolantT", "region2_coolantT"],
            "np_2b": ["oiltemp1", "oiltemp2", "oiltemp3"],
            "np_2c": ["reg1_Intake_Temp", "reg2_Intake_Temp", "reg3_Intake_Temp"],
            "np_3a": ["fueltemp1", "fueltemp2", "fueltemp3"],
            "np_3c": ["reg1_gas_railpressure", "reg2_gas_railpressure", "reg3_gas_railpressure"],
            "np_3f": ["reg1_Mixture_selfpoor", "reg2_Mixture_selfpoor", "reg3_Mixture_selfpoor"],
            "np_3g": ["reg1_Mixture_selfrich", "reg2_Mixture_selfrich", "reg3_Mixture_selfrich"],
            "np_4d": ["reg1_Cat_Eff", "reg2_Cat_Eff", "reg3_Cat_Eff"],
            "np_5c": [
                "reg1_Intake_manifoldpressure",
                "reg2_Intake_manifoldpressure",
                "reg3_Intake_manifoldpressure",
            ],
        }
        for sheet_id, columns in expected.items():
            self.assertEqual(get_columns_for_sheet(series, group, sheet_id), columns)

    def test_403_np_calculated_sheet_units_and_vehicle_speed_bands(self):
        series = "S_WAY_NP_MY_2024"
        group = "IVECO_S_X_WAY_NP"

        self.assertEqual(
            get_columns_for_sheet(series, group, "np_engine_lifecycle"),
            ["engine_life_cycle"],
        )
        self.assertEqual(
            get_columns_for_sheet(series, group, "np_low_catalyst_efficiency"),
            ["Low_Cat_Eff_time", "Low_Cat_Eff_count"],
        )
        self.assertEqual(
            get_sheet_settings("np_average_vehicle_speed")["allowed_group_values"],
            {"Average_vehicle_speed_split": ["<20 km/h", "20-40 km/h"]},
        )
        self.assertEqual(
            get_sheet_settings("np_average_vehicle_speed")["required_group_values"],
            {"Average_vehicle_speed_split": ["<20 km/h", "20-40 km/h"]},
        )
        self.assertEqual(
            get_sheet_settings("np_engine_lifecycle")["group_by"],
            ["engine_model", "mileage_range"],
        )
        self.assertEqual(
            get_sheet_settings("np_low_catalyst_efficiency")["group_by"],
            ["engine_model", "mileage_range"],
        )

        calculated_columns = {
            "np_catalyst_temperature": ["Catalyst_temp_860"],
            "np_coolant_temperature_high": ["Coolant_temp_high_104"],
            "np_oil_temperature_high": ["Oil_temp_high_120"],
            "np_boost_pressure_high": ["Boost_pressure_high_25"],
            "np_ambient_pressure_low": ["Ambient_pressure_low_850"],
        }
        for sheet_id, columns in calculated_columns.items():
            self.assertEqual(get_columns_for_sheet(series, group, sheet_id), columns)
            self.assertEqual(get_sheet_settings(sheet_id)["duration_columns"], [])

        for sheet_id in ("np_3c", "np_3f", "np_3g", "np_4d"):
            self.assertEqual(
                get_sheet_settings(sheet_id)["group_by"],
                ["engine_model", "mileage_range"],
            )

        expected_names = {
            "np_engine_lifecycle": "Engine Life Cycle (%)",
            "np_engine_overspeed": "Engine overspeed >2660 rpm",
            "np_catalyst_temperature": "Catalyst temperature >860 C",
            "np_low_catalyst_efficiency": "Low Catalyst Efficiency",
            "np_coolant_temperature_high": "High coolant temp >104 C",
            "np_oil_temperature_high": "High oil temp >120 C",
            "np_boost_pressure_high": "High boost pressure >2.5 bar",
            "np_ambient_pressure_low": "Low ambient pressure <850 mbar",
        }
        for sheet_id, expected_name in expected_names.items():
            self.assertEqual(get_sheet_settings(sheet_id)["name"], expected_name)
            self.assertLessEqual(len(expected_name), 31)

    def test_sheet_names_follow_latest_catalog_with_excel_safe_abbreviations(self):
        expected_names = {
            "1a": "1a) Engine Torque-Speed",
            "1b": "1b) Engine Torque-Veh Speed",
            "2a": "2a) Oil Pressure Analysis",
            "3c_1": "3c) Fuel pre-filter pressure",
            "3c": "3d) Intake air temperature",
            "3d": "3e) Intake air pressure",
            "3e": "3f) Flap actuator position",
            "3f": "3g) EGR actuator position",
            "4a_1": "4a_1) Catalyst eff [g-kWh]",
            "4a": "4a_2) Catalyst eff [g-kWh]",
            "4e": "4e) Urea deposit accumulation",
            "4f": "4f) AdBlue pressure pump",
            "4g_doc_upstream_temperature": "4g) DOC upstream temperature",
            "4h_scr_upstream_temperature": "4h) SCR upstream temperature",
            "4i_scr_downstream_temperature": "4i) SCR downstream temperature",
            "5c": "5c) DPF differential pressure",
        }

        for sheet_id, expected_name in expected_names.items():
            self.assertEqual(get_sheet_settings(sheet_id)["name"], expected_name)
            self.assertLessEqual(len(expected_name), 31)

    def test_default_sheet_order_matches_catalog_sequence_for_3c_to_4i(self):
        sheet_ids = get_default_sheet_ids()

        self.assertNotIn("4h", sheet_ids)
        self.assertLess(sheet_ids.index("3c_1"), sheet_ids.index("3c"))
        self.assertLess(sheet_ids.index("3c"), sheet_ids.index("3d"))
        self.assertLess(sheet_ids.index("4f"), sheet_ids.index("4g_doc_upstream_temperature"))
        self.assertLess(sheet_ids.index("4g_doc_upstream_temperature"), sheet_ids.index("4h_scr_upstream_temperature"))
        self.assertLess(sheet_ids.index("4h_scr_upstream_temperature"), sheet_ids.index("4i_scr_downstream_temperature"))
        self.assertLess(sheet_ids.index("4i_scr_downstream_temperature"), sheet_ids.index("5a_dpf"))

    def test_sheet_name_can_change_by_series_context(self):
        self.assertEqual(
            get_sheet_name_for_context("S_WAY_AT_AD_MY_2024", "IVECO_S_WAY", "2a"),
            "2a_1) Oil pressure",
        )
        self.assertEqual(
            get_sheet_name_for_context("X-WAY MY24 AT/AD_V1.6.4 C9", "IVECO_X-WAY", "2a"),
            "2a) Oil Pressure Analysis",
        )


if __name__ == "__main__":
    unittest.main()
