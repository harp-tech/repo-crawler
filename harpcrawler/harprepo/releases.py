import re
import pandas as pd

import packaging.version as version
from typing import List, Dict, Optional


_releases_regex = {
    "FirmwareVersion": "fw(.*)-harp*",
    "HarpProtocolVersion": "harp(.*)",
    "HardwareVersion": "pcb(.*)"
}


def parse_release(release_string: str, release_type: str) -> Optional[version.Version]:

    match release_type:
        case "FirmwareVersion":
            m = (re.search(_releases_regex["FirmwareVersion"], release_string))
            found = m.group(1) if m else None

        case "HarpProtocolVersion":
            m = (re.search(_releases_regex["HarpProtocolVersion"], release_string))
            found = m.group(1) if m else None

        case "HardwareVersion":
            m = (re.search(_releases_regex["HardwareVersion"], release_string))
            found = m.group(1) if m else None

        case _:
            raise NotImplementedError(
                f"Unknown release type: {release_type} in release {release_string}."
                )

    return version.parse(found) if found is not None else None

def get_releases(release_string: str, target_releases: Optional[List[str]] = None) -> Dict[str,version.Version]:
    if target_releases is None:
        target_releases = list(_releases_regex.keys())
    this_rel_versions = {}
    has_rel = False
    for target_rel in target_releases:
        this_rel_versions[target_rel] = parse_release(release_string, target_rel)
        if this_rel_versions[target_rel]:
            has_rel = True
    if not has_rel:
        raise AssertionError(f"No valid release found for release string {release_string}")
    return this_rel_versions

def get_release_table(release_list: List[str], target_releases: Optional[List[str]] = None) -> pd.DataFrame:
    if target_releases is None:
        target_releases = list(_releases_regex.keys())
    rows = []
    for rel in release_list:
        row = get_releases(rel, target_releases)
        row["Release"] = rel
        rows.append(row)
    if len(rows) == 0:
        row = {k: None for k in target_releases}
        row["Release"] = "NoReleaseFound"
        rows = [row]
    release_table = pd.DataFrame(rows)
    release_table.set_index("Release", inplace=True)
    return release_table

def get_latest_release(release_table: pd.DataFrame) -> Dict[str, Optional[version.Version]]:
    latest_rel = {}
    for (release_type, release_ver) in release_table.items():
        ver_list = [r for r in release_ver if r is not None]
        if len(ver_list) > 0:
            latest_rel[release_type] = max(ver_list)
        else:
            latest_rel[release_type] = None

    return latest_rel
