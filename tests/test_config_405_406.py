import unittest

from engine_config import get_columns_for_sheet, is_new_layout_series
from engine_loader import get_export_file_name, get_table_path
from run_local_sample import MISSION_ORDER, prepare_excel_dataframe

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


if __name__ == "__main__":
    unittest.main()
