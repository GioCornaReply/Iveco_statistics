import unittest

from engine_config import (
    get_columns_for_sheet,
    get_default_sheet_ids,
    get_sheet_name_for_context,
    get_sheet_settings,
)
from engine_loader import get_export_file_name, get_metadata_for_config, get_table_path

SERIES_410 = "S_WAY_NP_MY24_C13"
GROUP_410 = "IVECO_S_X_WAY_NP"


class Config410Test(unittest.TestCase):
    def test_410_routes_to_mission_test_unity_catalog_table(self):
        self.assertEqual(
            get_table_path(410),
            "u_truck_analyzer_p.mission_test_statistics.fat_table_410",
        )

    def test_410_metadata_and_export_name_follow_np_naming(self):
        self.assertEqual(
            get_metadata_for_config({410}),
            ("MISSION_TEST", GROUP_410, SERIES_410),
        )
        self.assertEqual(
            get_export_file_name(GROUP_410, {410}),
            "Statistics_HEAVY_SWAY_NP_410_dataset.xlsx",
        )

    def test_410_splits_1a_by_fly_recorder_tag_like_409(self):
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "np_1a_1"),
            ["region3_torque_enginespeed", "region4_torque_enginespeed"],
        )
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "np_409_1a_2"),
            [
                "region1_torque_enginespeed",
                "region2_torque_enginespeed",
                "region3bis_torque_enginespeed",
                "region4bis_torque_enginespeed",
            ],
        )
        for sheet_id in ("np_1a_1", "np_409_1a_2"):
            self.assertEqual(
                get_sheet_settings(sheet_id)["group_by"],
                ["engine_model", "power", "mission"],
            )

    def test_410_skips_diesel_1a_sheets(self):
        for sheet_id in ("1a", "1a_2"):
            self.assertEqual(get_columns_for_sheet(SERIES_410, GROUP_410, sheet_id), [])

    def test_410_uses_lng_and_cng_fuel_sheets(self):
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "fuel_lng"),
            [
                "average_fuel_consumption_kml",
                "average_fuel_consumption_l100km",
                "Tot_fuel_LNG",
            ],
        )
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "fuel_cng"),
            [
                "average_fuel_consumption_CNG_kml",
                "average_fuel_consumption_CNG_l100km",
                "Tot_fuel_CNG",
            ],
        )

    def test_410_regions_and_engine_speed_follow_template_names(self):
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "1b"),
            [
                "region1_torque_vehiclespeed",
                "region2_torque_vehiclespeed",
                "region3_torque_vehiclespeed",
                "region4_torque_vehiclespeed",
                "region5_torque_vehiclespeed",
            ],
        )
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "1c"),
            ["engine_revolutions_OK", "engine_revolutions_medium", "engine_revolutions_high"],
        )
        # 403 e 409 mantengono i propri nomi.
        self.assertEqual(
            get_columns_for_sheet("S_WAY_NP_MY_2024", GROUP_410, "1c")[0],
            "eng_speed_1",
        )
        self.assertEqual(
            get_columns_for_sheet("S_WAY_AS_NP_MY22_LATAM", "IVECO_S_WAY", "1b")[0],
            "region1_torque_vehiclespeed",
        )

    def test_410_inherits_403_columns_where_it_has_no_own_rule(self):
        # Le colonne della 403 sono il default NP MY24: la 410 le riceve dove il
        # template non ha una regola propria; gli sheet in piu' si tolgono a mano.
        for sheet_id in (
            "urea_consumption_pct",
            "urea_consumption_l100km",
            "urea_consumption_l100km_2",
            "average_crank_per_hour",
            "up_downstream_temperatures",
            "catalyst_info_v2",
            "max_values",
            "turbocharger_revolutions",
            "3b",
            "3d",
            "5b",
        ):
            self.assertEqual(
                get_columns_for_sheet(SERIES_410, GROUP_410, sheet_id),
                get_columns_for_sheet("S_WAY_NP_MY_2024", GROUP_410, sheet_id),
                sheet_id,
            )
        # Sheet MY24 gia' esclusi per la 403 restano esclusi anche per la 410.
        for sheet_id in ("2a", "2b"):
            self.assertEqual(get_columns_for_sheet(SERIES_410, GROUP_410, sheet_id), [], sheet_id)
        # np_4d duplica np_409_4d (stesse colonne reg1..3_Cat_Eff): esporta solo quello.
        self.assertEqual(get_columns_for_sheet(SERIES_410, GROUP_410, "np_4d"), [])

    def test_410_receives_the_np_my24_kpi_sheets_and_catalyst_split(self):
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "np_engine_lifecycle"),
            ["engine_life_cycle"],
        )
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "np_409_4a_1"),
            ["catalyst_temperature_over_900_pct"],
        )
        self.assertEqual(
            get_columns_for_sheet(SERIES_410, GROUP_410, "np_409_4d"),
            ["reg1_Cat_Eff", "reg2_Cat_Eff", "reg3_Cat_Eff"],
        )

    def test_410_sheet_names_use_np_series_labels(self):
        self.assertEqual(
            get_sheet_name_for_context(SERIES_410, GROUP_410, "np_engine_overspeed"),
            "Engine Overspeed",
        )

    def test_410_does_not_leak_into_403_series(self):
        self.assertEqual(
            get_columns_for_sheet("S_WAY_NP_MY_2024", GROUP_410, "np_409_1a_2"),
            [],
        )
        self.assertIn("np_409_1a_2", get_default_sheet_ids())
