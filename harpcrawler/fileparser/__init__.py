import markdown

from enum import Enum
from typing import Optional

from github import Repository

from harprepo import HarpRepo
import fileparser.readme as readme


class RepoFileType(Enum):
    NONE = None
    README = "README"


def validate_content(
    repo: Repository.Repository | HarpRepo,
    path: str,
    filetype: RepoFileType,
    fail_on_warnings=False) -> any:

    if isinstance(repo, HarpRepo):
        repo = repo.repository

    match filetype:
        case RepoFileType.README:
            return readme.validate(repo, path, fail_on_warnings=fail_on_warnings)
        case _:
            raise NotImplementedError(
                f"File parser not implemented for {str(filetype)} file type."
                )
