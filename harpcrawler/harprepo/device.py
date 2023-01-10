import pandas as pd

from github import Repository
from harprepo import HarpRepo, RepositoryType
from typing import List


class DeviceRepo(HarpRepo):

    def __init__(self,
    repository: Repository.Repository,
    template: Repository.Repository | None = None) -> None:
        super().__init__(
            repository=repository)
        self.repository_type = RepositoryType.DEVICE
        self.template = template

    def exist_harpfiles(self, path_list: list = None):
        if path_list is None:
            if self.template is not None:
                path_list = self.template.filetree
            else:
                raise ValueError("A valid template target must be provided!")
        return (super().exist_harpfiles(path_list))


class TemplateDeviceRepo(DeviceRepo):
        def __init__(self, repository: Repository.Repository) -> None:
            super().__init__(repository=repository)
            self.populate_repo()
            self.diagnosis_table =  None

        def run_diagnosis(self, repos_to_validate: List[DeviceRepo]) -> None:
            diagnosis_table = pd.DataFrame(columns = self.filetree)
            diagnosis_table = diagnosis_table.astype('bool')

            for repo in repos_to_validate:
                diagnosis_table = pd.concat([diagnosis_table,\
                    pd.DataFrame(repo.exist_harpfiles(), index = [repo.repository.full_name.split("/")[-1]])\
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