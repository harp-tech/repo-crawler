import pandoc

from github import Repository
from pandoc.types import Image, Header
from typing import List, Tuple

_ASSETS_PCB_PATH = "./Assets/pcb.png"

def validate(
    repository: Repository.Repository,
    path: str,
    fail_on_warnings = False)-> Tuple[bool, List[str]]:

    content = repository.get_contents(path)
    _validation, _warnings = integraty_test(
        content.decoded_content,
        opt_filename=path,
        fail_on_warnings=fail_on_warnings)
    return _validation, _warnings

def integraty_test(
    decoded_content,
    opt_filename = '',
    fail_on_warnings = False) -> Tuple[bool, List[str]]:

    is_fail = True
    parsed_doc = pandoc.read(decoded_content)

    warnings = []
    headers = []
    for elt in pandoc.iter(parsed_doc):
        if isinstance(elt, Header):
            headers.append([elt[0], elt[1][0]])

    ## Check existence of a pcb figure
    images = []
    for elt in pandoc.iter(parsed_doc):
        if isinstance(elt, Image):
            images.append(elt)
    if len(images) == 0:
        warnings.append(f"No figures references found in {opt_filename}")
    _is_asset_found = False
    for im in images:
        if _ASSETS_PCB_PATH in im[2][0]:
            _is_asset_found=True
            break
    if not(_is_asset_found):
        warnings.append(f"Missing PCB figure in {_ASSETS_PCB_PATH}")

    if (fail_on_warnings and (len(warnings) > 0)):
        is_valid = False

    return is_fail, warnings