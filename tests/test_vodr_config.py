from engine_loader import get_table_path
from vodr_config import (
    DEFAULT_VODR_MT_CONFIGS,
    config_mt_from_vodr,
    generated_percentage_column,
    get_vodr_export_file_name,
    get_vodr_report_sheets,
)
from vodr_pipeline import parse_config_text


def test_vodr_statistics_configs_use_unity_catalog_tables():
    for config in (33, 49, 50, 51, 52, 53):
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


def test_vodr_export_file_name_is_stable():
    assert get_vodr_export_file_name({52}) == "VODR_52_new_thresholds.xlsx"
    assert get_vodr_export_file_name({50, 51}) == "VODR_50_51_new_thresholds.xlsx"
