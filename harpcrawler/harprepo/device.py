import pandas as pd
from typing import List, Optional, Dict, Callable
from github import Repository

from harpcrawler.harprepo import HarpRepo, RepositoryType
import harpcrawler.fileparser as fileparser

import harpcrawler.harprepo.releases as releases

_expected_releases = ["FirmwareVersion","HarpProtocolVersion","HardwareVersion"]

_name_consistency_checks = [
lambda x : f"Firmware/{x.lower()}",
lambda x : f"Firmware/{x.lower()}.atsln",
lambda x : f"Firmware/{x.lower()}/{x.lower()}.cproj"
]

class DeviceRepo(HarpRepo):

    def __init__(
        self,
        repository: Repository.Repository,
        template: Optional[Repository.Repository] = None) -> None:

        super().__init__(
            repository=repository, template=template)
        self.repository_type = RepositoryType.DEVICE
        self.latest_releases = None

    def exist_harpfiles(self, path_list: list = None, ignore_case: bool = False):
        if path_list is None:
            if self.template is not None:
                path_list = self.template.filetree
            else:
                raise ValueError("A valid template target must be provided!")
        return (super().exist_harpfiles(path_list=path_list, ignore_case=ignore_case))

    def get_latest_releases(self, target_releases: Optional[List[str]] = None):
        if target_releases is None:
            target_releases = _expected_releases
        all_releases = [x.tag_name for x in self.repository.get_releases()]
        releases_table = releases.get_release_table(all_releases, target_releases)
        latest_releases = releases.get_latest_release(releases_table)
        self.latest_releases = latest_releases

    def check_name_consistency(
        self,
        check_list: Optional[List[Callable]] = None,
        remove_test_pass: bool = True,
        ignore_case: bool = True) -> Dict[str, bool]:
        if check_list is None:
            check_list = _name_consistency_checks
        device_name = self.repository.name.split(".")[1].lower()
        exists_path = self.exist_harpfiles(
            path_list=[x(device_name) for x in check_list],
            ignore_case=ignore_case)
        if remove_test_pass:
            test_fails = {k:v for (k,v) in exists_path.items() if v is False}
            return test_fails
        else:
            return exists_path


class TemplateDeviceRepo(DeviceRepo):
        def __init__(self, repository: Repository.Repository) -> None:
            super().__init__(repository=repository)
            self.populate_repo()
            self.diagnosis_table =  None

        def run_diagnosis(
            self,
            repos_to_validate: List[DeviceRepo],
            files_to_validate: List[str] = ["README.md"]) -> None:

            diagnosis_table = pd.DataFrame(columns = self.filetree)
            diagnosis_table = diagnosis_table.astype('bool')

            for repo in repos_to_validate:
                _exists = repo.exist_harpfiles()
                if repo.latest_releases is None:
                    repo.get_latest_releases()
                _exists = repo.latest_releases | _exists

                ## Warnings
                # Warnings reporting the content of specific files
                _exists["ContentWarnings"] = [fileparser.validate_content(
                    repository=repo,
                    template_repository=self,
                    template_files=files_to_validate)]

                # Warnings reporting device naming conventions
                _exists["NamingWarnings"] = [list(repo.check_name_consistency(remove_test_pass=True).keys())]

                diagnosis_table = pd.concat([diagnosis_table,\
                    pd.DataFrame(_exists, index = [repo.repository.full_name.split("/")[-1]])\
                        ], axis=0, ignore_index=False)

            self.diagnosis_table = diagnosis_table

        def print_diagnosis(self) -> pd.DataFrame:
            if self.diagnosis_table is None:
                raise ValueError("A valid diagnosis table does not exist. \
                    Try to use the run_diagnosis() method first.")
            else:
                diagnosis_table = self.diagnosis_table.copy()
                cols = diagnosis_table.columns.to_list()
                cols.insert(0,'Device')
                diagnosis_table['Device'] = diagnosis_table.index
                diagnosis_table = diagnosis_table[cols]
                diagnosis_table = diagnosis_table.replace({True: '\u2705', False: '\u274C'})
                return diagnosis_table