import pandas as pd
from typing import List, Optional, Dict, Callable, Tuple
from github import Repository

from harpcrawler.harprepo import HarpRepo, RepositoryType
import harpcrawler.fileparser as fileparser
import harpcrawler.harprepo.releases as releases
import packaging.version as version


_expected_releases = [
    "FirmwareVersion",
    "HarpProtocolVersion",
    "HardwareVersion",
    "AppVersion",
    "ApiVersion",
]

_name_consistency_checks = [
    lambda x: f"Firmware/{x.lower()}",
    lambda x: f"Firmware/{x.lower()}.atsln",
    lambda x: f"Firmware/{x.lower()}/{x.lower()}.cproj",
]


class DeviceRepo(HarpRepo):
    def __init__(
        self,
        repository: Repository.Repository,
        template: Optional[Repository.Repository] = None,
    ) -> None:
        super().__init__(repository=repository, template=template)
        self.repository_type = RepositoryType.DEVICE
        self.latest_releases = None

    def exist_harpfiles(self, path_list: list = None, ignore_case: bool = False):
        if path_list is None:
            if self.template is not None:
                path_list = self.template.filetree
            else:
                raise ValueError("A valid template target must be provided!")
        return super().exist_harpfiles(path_list=path_list, ignore_case=ignore_case)

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
        ignore_case: bool = True,
    ) -> Dict[str, bool]:
        if check_list is None:
            check_list = _name_consistency_checks
        device_name = self.repository.name.split(".")[1].lower()
        exists_path = self.exist_harpfiles(
            path_list=[x(device_name) for x in check_list], ignore_case=ignore_case
        )
        if remove_test_pass:
            test_fails = {k: v for (k, v) in exists_path.items() if v is False}
            return test_fails
        else:
            return exists_path

    def get_yml_schema_metadata(
        self, filename: str = "device.yml"
    ) -> Tuple[bool, Dict[str, str]]:
        _is_file = all(
            [x is True for x in self.exist_harpfiles(path_list=[filename]).values()]
        )
        if not _is_file:
            metadata = {
                "schema_device": f"{filename} not found!",
                "schema_whoAmI": f"{filename} not found!",
                "schema_firmwareVersion": f"{filename} not found!",
                "schema_hardwareTargets": f"{filename} not found!",
            }
            return (False, metadata)
        else:
            yml = fileparser.parse_yml(
                self.repository.get_contents(filename).decoded_content
            )
            metadata = {
                "schema_device": yml["device"],
                "schema_whoAmI": yml["whoAmI"],
                "schema_firmwareVersion": yml["firmwareVersion"],
                "schema_hardwareTargets": yml["hardwareTargets"],
            }
            return (True, metadata)


class TemplateDeviceRepo(DeviceRepo):
    def __init__(self, repository: Repository.Repository) -> None:
        super().__init__(repository=repository)
        self.populate_repo()
        self.diagnosis_table = None

    def run_diagnosis(
        self,
        repos_to_validate: List[DeviceRepo],
        files_to_validate: List[str] = ["README.md"],
    ) -> None:
        diagnosis_table = pd.DataFrame(columns=self.filetree)
        diagnosis_table = diagnosis_table.astype("bool")

        for repo in repos_to_validate:
            try:
                output_table = {}

                # Check if the device.yml file exists and get the WHOAMI
                _yml_filename = "device.yml"
                has_yml, yml_metadata = repo.get_yml_schema_metadata(
                    filename=_yml_filename
                )
                if has_yml:
                    output_table |= yml_metadata
                else:
                    output_table |= yml_metadata
                    print(
                        f"Warning: {repo.repository.full_name} does not have a {_yml_filename} file!"
                    )

                # Check releases
                output_table |= repo.exist_harpfiles()
                if repo.latest_releases is None:
                    repo.get_latest_releases()
                output_table |= repo.latest_releases | output_table

                # Match firmware releases
                if (has_yml) and (output_table["FirmwareVersion"] is not None):
                    output_table["HasUpdatedFirmware"] = version.parse(
                        output_table["schema_firmwareVersion"]
                    ) == (output_table["FirmwareVersion"])
                else:
                    output_table["HasUpdatedFirmware"] = False

                # Warnings
                # Warnings reporting the content of specific files
                output_table["ContentWarnings"] = [
                    fileparser.validate_content(
                        repository=repo,
                        template_repository=self,
                        template_files=files_to_validate,
                    )
                ]

                # Warnings reporting device naming conventions
                output_table["NamingWarnings"] = [
                    list(repo.check_name_consistency(remove_test_pass=True).keys())
                ]

                # Releases warnings

                diagnosis_table = pd.concat(
                    [
                        pd.DataFrame(
                            output_table,
                            index=[repo.repository.full_name.split("/")[-1]],
                        ),
                        diagnosis_table,
                    ],
                    axis=0,
                    ignore_index=False,
                )
            except Exception as err:
                print(f"Error while diagnosing {repo.repository.full_name}: {err}")

        self.diagnosis_table = diagnosis_table

    def print_diagnosis(self) -> pd.DataFrame:
        if self.diagnosis_table is None:
            raise ValueError(
                "A valid diagnosis table does not exist. \
                Try to use the run_diagnosis() method first."
            )
        else:
            diagnosis_table = self.diagnosis_table.copy()
            cols = diagnosis_table.columns.to_list()
            cols.insert(0, "Device")
            diagnosis_table["Device"] = diagnosis_table.index
            diagnosis_table = diagnosis_table[cols]
            diagnosis_table = diagnosis_table.replace({True: "\u2705", False: "\u274C"})
            return diagnosis_table
