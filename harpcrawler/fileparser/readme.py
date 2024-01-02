import pandoc

from typing import List
from pandoc.types import Image, Header

from harpcrawler.harprepo import HarpRepo


_assets_pcb_path = "./Assets/pcb.png"
_headers_to_ignore = ["harp-device", "harp-peripheral"]


def validate(
    filepath: str, repository: HarpRepo, template_repository: HarpRepo
) -> List[str]:
    warnings = []
    try:
        content = repository.repository.get_contents(filepath).decoded_content
        template_content = template_repository.repository.get_contents(
            filepath
        ).decoded_content

        parsed_content = pandoc.read(content)
        parsed_template_content = pandoc.read(template_content)

        # Run tests
        warnings.append(test_headers(parsed_content, parsed_template_content))
        warnings.append(test_pcb_image(parsed_content))
    except:
        warnings.append("Could not parse file.")
    return warnings


def test_headers(parsed_content, parsed_template_content) -> List[str]:
    ## Find all expected headers in the template
    template_headers = []
    for elt in pandoc.iter(parsed_template_content):
        if isinstance(elt, Header):
            template_headers.append([elt[0], elt[1][0]])

    ## Find all headers in tested repository
    tested_headers = []
    for elt in pandoc.iter(parsed_content):
        if isinstance(elt, Header):
            tested_headers.append([elt[0], elt[1][0]])

    report = []
    _ = [
        report.append(h)
        for h in template_headers
        if ((h not in tested_headers) and (h[1] not in _headers_to_ignore))
    ]
    str_report = [f"Header issue in {h}" for h in report]
    return str_report


def test_pcb_image(parsed_content) -> List[str]:
    ## Check existence of a pcb figure
    report = []
    images = []
    for elt in pandoc.iter(parsed_content):
        if isinstance(elt, Image):
            images.append(elt)
    if len(images) == 0:
        report.append("No figures references found.")
    _is_asset_found = False
    for im in images:
        if _assets_pcb_path in im[2][0]:
            _is_asset_found = True
            break
    if not (_is_asset_found):
        report.append(
            f"Could not find figure reference to expected path ({_assets_pcb_path})."
        )
    return report
