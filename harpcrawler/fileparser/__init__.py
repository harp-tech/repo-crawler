from typing import List, Optional

from harpcrawler.fileparser import readme
from harpcrawler.harprepo import HarpRepo


def validate_content(
    repository: HarpRepo,
    template_repository: Optional[HarpRepo],
    template_files: List[str] = [],
) -> List[str]:
    ## If no template is provided try to get the default
    if template_repository is None:
        template_repository = repository.template
    warnings = {}
    for file in template_files:
        match file:
            case "README.md":
                this_warnings = readme.validate(
                    filepath=file,
                    repository=repository,
                    template_repository=template_repository,
                )
            case _:
                raise NotImplementedError(
                    f"File validation not implemented for {str(file)}."
                )
        if any(this_warnings):
            warnings[file] = this_warnings
    return warnings


def parse_yml(content: str) -> dict:
    import yaml
    from yaml import Loader

    try:
        return yaml.load(content, Loader)
    except yaml.YAMLError as exception:
        raise exception
