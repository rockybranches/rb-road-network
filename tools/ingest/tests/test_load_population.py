import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from load_population import load, match_row, names_agree, normalize  # noqa: E402


def county(geoid, ns, name, kind="County", state="GA"):
    return {
        "geoid": geoid,
        "countyns": ns,
        "name": name,
        "namelsad": f"{name} {kind}",
        "stusps": state,
    }


GA = [
    county(13087, 352234, "Decatur"),
    county(13089, 1687424, "DeKalb"),
    county(13223, 349912, "Paulding"),
    county(13225, 343153, "Peach"),
]


def test_normalize_strips_source_quoting():
    assert normalize("'Prince George''s'") == "prince george's"
    assert normalize("  Lake  Of The Wood ") == "lake of the wood"


def test_names_agree_handles_city_suffix_and_truncation():
    baltimore_city = county(24510, 1, "Baltimore", kind="city", state="MD")
    assert names_agree("Baltimore City", baltimore_city)
    woods = county(27077, 2, "Lake of the Woods", state="MN")
    assert names_agree("Lake Of The Wood", woods)
    assert not names_agree("Lake", woods)  # too short to trust as a prefix


def test_clean_row_matches_by_code():
    assert match_row(349912, "Paulding", GA)[:2] == ("ok", GA[2])


def test_swapped_codes_are_resolved_by_name():
    status, found, note = match_row(352234, "DeKalb", GA)
    assert (status, found["geoid"]) == ("fixed", 13089)
    assert "Decatur County" in note
    assert match_row(1687424, "Decatur", GA)[1]["geoid"] == 13087


def test_duplicated_code_is_resolved_by_name():
    # Peach carries Paulding's code in the source.
    status, found, _ = match_row(349912, "Peach", GA)
    assert (status, found["geoid"]) == ("fixed", 13225)


def test_unplaceable_rows_are_rejected():
    assert match_row(999, "Nowhere", GA)[0] == "rejected"
    twins = [
        county(51059, 1, "Fairfax", state="VA"),
        county(51600, 2, "Fairfax", kind="city", state="VA"),
    ]
    assert match_row(999, "Fairfax", twins) == (
        "rejected",
        None,
        "code 999; name is ambiguous",
    )


def test_load_reads_state_files_and_reports(tmp_path):
    (tmp_path / "ga.csv").write_text(
        "County NS Code,County,2010,2015,Unnamed: 4\n"
        "352234,DeKalb,692443,734434.0,\n"
        "1687424,Decatur,27842,27220,\n"
        "349912,Paulding,142324,152238,\n"
        "349912,Peach,27695,\n"
    )
    (tmp_path / "ak.csv").write_text("County NS Code,County,2010\n1,Somewhere,5\n")
    rows, report = load(GA, tmp_path)
    assert (13089, 2010, 692443) in rows and (13089, 2015, 734434) in rows
    assert (13087, 2010, 27842) in rows
    assert (13225, 2010, 27695) in rows and (13225, 2015, None) not in rows
    assert report["ok"] == 1 and len(report["fixed"]) == 3
    assert report["skipped_files"] == ["ak.csv"]
    assert report["counties_without_population"] == []
