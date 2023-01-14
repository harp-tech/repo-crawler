import harprepo
import fileparser.readme as readme
from typing import List

def validate_content(
    repository: harprepo.HarpRepo,
    template_repository: harprepo.device.TemplateDeviceRepo | harprepo.peripheral.TemplatePeripheralRepo,
    template_files: List[str] = []) -> List[str]:

    warnings = {}
    for file in template_files:
        match file:
            case "README.md":
                this_warnings = readme.validate(
                    filepath=file,
                    repository=repository,
                    template_repository=template_repository)
            case _:
                raise NotImplementedError(
                    f"File validation not implemented for {str(file)}."
                    )
        if any(this_warnings):
            warnings[file] = this_warnings
    return warnings