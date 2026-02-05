from __future__ import annotations

import requests
import yaml
import os

from github.GithubException import UnknownObjectException
from typing import Dict, Optional
from github import Github, Repository
from urllib.parse import urlparse
from pydantic import BaseModel


class Device(BaseModel):
    authors: str = ""
    name: str
    copyright: Optional[str] = None
    projectUrl: Optional[str] = None
    repositoryUrl: Optional[str] = None


class WhoAmIList(BaseModel):
    devices: Dict[int, Device]


def read_whoami_file(
    file_path: str = "https://raw.githubusercontent.com/harp-tech/whoami/refs/heads/main/whoami.yml",
    is_remote: bool = True,
) -> WhoAmIList:
    if is_remote:
        response = requests.get(file_path, allow_redirects=True)
        content = response.content.decode("utf-8")
        content = yaml.safe_load(content)
    else:
        with open(file_path, "r") as stream:
            content = yaml.safe_load(stream)
    print(content)
    return WhoAmIList(**content)


class DeviceUrl:
    url: str
    hostname: str
    is_github: bool
    organization: str
    repository: str
    github_client: Github

    def __init__(self, url: str, github_client: Github):
        _url = urlparse(url)
        self.url = _url
        self.hostname = _url.hostname
        self.is_github = _url.hostname == "github.com"
        _address = os.path.split(_url.path.strip("/"))
        self.organization = _address[0]
        self.repository = _address[1]
        self.github_client = github_client

    def get_repo(self) -> Repository:
        if self.is_github:
            try:
                repo = self.github_client.get_repo(
                    f"{self.organization}/{self.repository}"
                )
                return repo
            except UnknownObjectException:
                print(f"Repository {self.organization}/{self.repository} not found!")
                return None
        else:
            raise NotImplementedError("Only GitHub repositories are supported")
