from github import Github, Repository
from harprepo import HarpRepo, RepositoryType


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