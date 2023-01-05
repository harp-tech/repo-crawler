from github import Github, Repository
from enum import Enum


class DeviceFiles(Enum):
    README = "README.md"
    GITIGNORE = ".gitignore"
    FIRMWARE_GITIGNORE = "Firmware/.gitignore"
    HARDWARE_GITIGNORE = "Hardware/.gitignore"
    INTERFACES_GITIGNORE = "Interfaces/.gitignore"

class RepositoryType(Enum):
    GENERIC = "GENERIC"
    PERIPHERAL = "Peripheral"
    DEVICE = "Device"

class HarpRepo():
    def __init__(self,
        repository: Repository.Repository) -> None:

        self.repository = repository
        self.filetree = []
        self.repository_type = RepositoryType.GENERIC

    def populate_repo(self):
        self.filetree = []
        contents = self.repository.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repository.get_contents(file_content.path))
            else:
                self.filetree.append(file_content.path)

    def get_readme(self, opt_path = DeviceFiles.README):
        file = self.repository.get_contents(opt_path)
        return file

    def exist_harpfiles(self, path_list):
        return ({file : file in self.filetree for file in path_list})

    def __repr__(self) -> str:
        return self.__str__()
    def __str__(self) -> str:
        return(str(self.repository))

class DeviceRepo(HarpRepo):

    def __init__(self, repository: Repository.Repository) -> None:
        super().__init__(repository=repository)
        self.repository_type = RepositoryType.DEVICE

    def exist_harpfiles(self, path_list = None):
        if path_list is None:
            return ({file : file.value in self.filetree for file in DeviceFiles})
        else:
            return (super().exist_harpfiles(path_list))

class PeripheralRepo(HarpRepo):

    def __init__(self, repository: Repository.Repository) -> None:
        super().__init__(repository=repository)
        self.repository_type = RepositoryType.PERIPHERAL

