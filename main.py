#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from github import Github
import gspread_formatting as gsf
import pandas as pd

from harpcrawler.harprepo.device import DeviceRepo, TemplateDeviceRepo
from harpcrawler.harprepo.peripheral import PeripheralRepo, TemplatePeripheralRepo
from harpcrawler.gsheets import HarpSpreadsheet
from harpcrawler.harprepo.device_indexing import read_whoami_file, DeviceUrl

# Tokens
GITHUB_KEY = os.environ.get("CREDENTIAL_GITHUB", None)
GOOGLE_KEY = os.environ.get("CREDENTIAL_GOOGLE", None)

# Flags
ORGANIZATION = "harp-tech"
SPREADSHEET = "GitHarpCrawler"
PRINT_DIAGNOSIS = True
UPDATE_SPREADSHEET = True


def main():
    # Setup
    if UPDATE_SPREADSHEET:
        harpSpreadsheet = HarpSpreadsheet(spreadsheet=SPREADSHEET,
                                          credentials=GOOGLE_KEY)

    gh = Github(login_or_token=GITHUB_KEY)

    device_template = TemplateDeviceRepo(gh.get_repo(f"{ORGANIZATION}/device.template"))
    peripheral_template = TemplatePeripheralRepo(gh.get_repo(f"{ORGANIZATION}/peripheral.template"))

    harp_organization = gh.get_organization(ORGANIZATION)

    who_am_i_list = read_whoami_file(file_path="https://raw.githubusercontent.com/harp-tech/protocol/main/whoami.yml")
    who_am_i_df = pd.DataFrame([who_am_i_list.devices[whoami].model_dump() for whoami in who_am_i_list.devices], index=who_am_i_list.devices.keys())
    who_am_i_df["deviceUrl"] = who_am_i_df["repositoryUrl"].apply(lambda x: DeviceUrl(x, gh) if x else None)
    tracked_repositories = [repo for repo in [repo_url.get_repo() for repo_url in who_am_i_df["deviceUrl"] if repo_url] if repo]
    device_repos = [DeviceRepo(repo, device_template) for repo in tracked_repositories]

    device_template.run_diagnosis(repos_to_validate=device_repos)
    device_diagnosis = device_template.print_diagnosis().applymap(lambda x: str(x))

    if PRINT_DIAGNOSIS:
        print(device_diagnosis)
    if UPDATE_SPREADSHEET:
        harpSpreadsheet.open_spreadsheet()
        harpSpreadsheet.update_spreadsheet("devices", device_diagnosis)

    # Get all "Peripherals.*" repositories

    peripheral_repos = [PeripheralRepo(repo, peripheral_template)
                        for repo in harp_organization.get_repos()
                        if (("peripheral." in repo.full_name) and
                            not("template" in repo.full_name) and
                            not(repo.is_template) and not(repo.archived))]
    peripheral_template.run_diagnosis(repos_to_validate=peripheral_repos)
    peripherals_diagnosis = peripheral_template.print_diagnosis().applymap(lambda x: str(x))

    if PRINT_DIAGNOSIS:
        print(peripherals_diagnosis)
    if UPDATE_SPREADSHEET:
        harpSpreadsheet.open_spreadsheet()
        harpSpreadsheet.update_spreadsheet("peripherals", peripherals_diagnosis)

    return 0


if __name__ == "__main__":
    main()