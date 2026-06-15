import unittest

from engine_config import get_columns_for_sheet, get_sheet_settings, is_new_layout_series
from engine_loader import get_export_file_name, get_table_path
from run_local_sample import MILEAGE_RANGE_ORDER, MISSION_ORDER, prepare_excel_dataframe

import pandas as pd


class Config405406Test(unittest.TestCase):
    def test_new_configs_use_unity_catalog_mission_test_tables(self):
        for config in (405, 406, 408):
            self.assertEqual(
                get_table_path(config),
                f"u_truck_analyzer_p.mission_test_statistics.fat_table_{config}",
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
        self.assertEqual(get_sheet_settings("4e")["name"], "4e) Urea Deposit")
        self.assertEqual(
            get_columns_for_sheet("X-WAY MY24 AT/AD_V1.6.4 C9", "IVECO_X-WAY", "4e"),
            ["urea_dep_1", "urea_dep_2", "urea_dep_3", "urea_dep_4"],
        )
        self.assertEqual(get_sheet_settings("4f")["name"], "4f) AdBlue Pressure Pump")
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


if __name__ == "__main__":
    unittest.main()
