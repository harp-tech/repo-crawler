from typing import Optional
from github import Repository
from enum import Enum

class RepositoryType(Enum):
    GENERIC = "GENERIC"
    PERIPHERAL = "Peripheral"
    DEVICE = "Device"

class HarpRepo():
    def __init__(self,
        repository: Repository.Repository,
        template: Optional[Repository.Repository] = None) -> None:

        self.repository = repository
        self.template = template
        self.filetree = None
        self.repository_type = RepositoryType.GENERIC

    def populate_repo(self):
        self.filetree = []
        contents = self.repository.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                self.filetree.append(file_content.path)
                contents.extend(self.repository.get_contents(file_content.path))
            else:
                self.filetree.append(file_content.path)

    def exist_harpfiles(self, path_list):
        if self.filetree is None:
            self.populate_repo()
        return ({file : file in self.filetree for file in path_list})

    def __repr__(self) -> str:
        return self.__str__()
    def __str__(self) -> str:
        return(str(self.repository.full_name))




