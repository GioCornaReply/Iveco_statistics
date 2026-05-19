import unittest

from engine_config import get_columns_for_sheet, is_new_layout_series
from engine_loader import get_export_file_name, get_table_path


class Config405406Test(unittest.TestCase):
    def test_new_configs_use_unity_catalog_mission_test_tables(self):
        self.assertEqual(
            get_table_path(405),
            "u_truck_analyzer_p.mission_test_statistics.fat_table_405",
        )
        self.assertEqual(
            get_table_path(406),
            "u_truck_analyzer_p.mission_test_statistics.fat_table_406",
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


if __name__ == "__main__":
    unittest.main()
