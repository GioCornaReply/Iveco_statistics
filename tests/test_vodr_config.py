from engine_loader import get_table_path
from vodr_config import (
    DEFAULT_VODR_MT_CONFIGS,
    config_mt_from_vodr,
    generated_percentage_column,
    get_vodr_export_file_name,
    get_vodr_percentage_groups,
    get_vodr_report_sheets,
)
from vodr_pipeline import parse_config_text


def test_vodr_statistics_configs_use_unity_catalog_tables():
    for config in (33, 49, 50, 51, 52, 53, 54, 56):
        assert (
            get_table_path(config)
            == f"u_truck_analyzer_p.vodr_statistics.fat_table_{config}"
        )


def test_vodr_to_mission_test_mapping_keeps_legacy_groups():
    assert config_mt_from_vodr({5, 19}) == {260, 288, 300, 301, 335, 336}
    assert config_mt_from_vodr({20, 21}) == {286, 287, 302, 303, 335, 336}
    assert config_mt_from_vodr({52}) == DEFAULT_VODR_MT_CONFIGS


def test_vodr_widget_config_parser_accepts_commas_spaces_and_sets():
    assert parse_config_text("50, 51;52") == {50, 51, 52}
    assert parse_config_text({52}) == {52}


def test_vodr_report_config_uses_generated_percentage_columns():
    assert generated_percentage_column("Ped1", "1b") == "PED1_1B"

    sheets = {sheet["sheet_id"]: sheet for sheet in get_vodr_report_sheets({52})}
    assert sheets["4c"]["columns"] == [
        "TimeAutoWithVehicleMoving",
        "TimeSemiWithVehicleMoving",
        "TimeAutoSuspendWithVehicleMoving",
    ]

    legacy_sheets = {sheet["sheet_id"]: sheet for sheet in get_vodr_report_sheets({5, 19})}
    assert legacy_sheets["4c"]["columns"] == [
        "TimeAuto",
        "TimeSemi",
        "TimeAutoSuspendWithVehicleMoving",
    ]


def test_vodr_config_56_uses_customer_sheet_catalog():
    sheets = get_vodr_report_sheets({56})
    sheet_ids = [sheet["sheet_id"] for sheet in sheets]

    assert sheet_ids == [
        "complete_dataset",
        "2",
        "1",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "4a",
        "5a",
        "5b",
        "5c",
        "6a",
        "6b",
        "6c",
        "6d",
        "7a",
    ]

    sheets_by_id = {sheet["sheet_id"]: sheet for sheet in sheets}
    assert sheets_by_id["2"]["name"] == "2) Accelerator pedal position"
    assert sheets_by_id["2"]["columns"] == ["Ped1", "Ped2", "Ped3", "Ped4"]
    assert sheets_by_id["1"]["columns"] == [
        "LowIdle",
        "Lowload",
        "LowL",
        "HighFuelone",
        "Optcons",
        "Highspeedlow",
        "Highfueltre",
        "Highfuellast",
    ]
    assert sheets_by_id["5"]["columns"] == [
        "Weight7",
        "Weight20",
        "Weight25",
        "Weight30",
        "Weight40",
        "Weight55",
        "WeightFF",
    ]
    assert sheets_by_id["5c"]["columns"] == [
        "Soh20OFF",
        "Soh50OFF",
        "Soh70OFF",
        "Soh90OFF",
        "Soh100OFF",
        "Soh20ON",
        "Soh50ON",
        "Soh70ON",
        "Soh90ON",
        "Soh100ON",
    ]
    assert sheets_by_id["7a"]["columns"] == ["Aebs95"]
    assert sheets_by_id["7a"]["use_percentage_columns"] is False
    assert "average_kick_down" not in sheet_ids
    assert all(len(sheet["name"]) <= 31 for sheet in sheets)


def test_vodr_config_56_percentage_groups_match_customer_columns():
    groups = get_vodr_percentage_groups({56})

    assert groups["3"] == ["EngCool106", "Engcool110", "EngCol200"]
    assert groups["4"] == ["OilTemp114", "Oiltemp200"]
    assert groups["4a"] == [
        "GearR1",
        "GearN",
        "Gear1",
        "Gear2",
        "Gear3",
        "Gear4",
        "Gear5",
        "Gear6",
        "Gear7",
        "Gear8",
        "Gear9",
    ]
    assert groups["6d"] == [
        "Cur10",
        "Cur30",
        "Cur50",
        "Cur70",
        "Cur90",
        "Cur91",
        "Cureng10",
        "Cureng30",
        "Cureng50",
        "Cureng70",
        "Cureng90",
        "Cureng91",
    ]
    assert "7a" not in groups


def test_vodr_export_file_name_is_stable():
    assert get_vodr_export_file_name({52}) == "VODR_52_new_thresholds.xlsx"
    assert get_vodr_export_file_name({50, 51}) == "VODR_50_51_new_thresholds.xlsx"
