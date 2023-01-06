# GitHarpCrawler
Code to query and automatically generate assets from the harp-tech organization's repositories


## Getting started

### Setup a python environment
 -  Create a Conda environment using the latest `environment.yaml`

### Setup GitHub authentication (via [PyGitHub](https://github.com/PyGithub/PyGithub))

- `examples/GithubCredentials.py` should return a `string` with an authentication token from GitHub. Make sure the permissions are set correctly. This value will be used to instantiate a `GitHub` class:

```python
gh = Github(login_or_token=my_credentials())
```

### Setup Google Sheets authentication (via [gspread](https://docs.gspread.org/))

- [Follow these instructions](https://docs.gspread.org/en/v5.7.0/oauth2.html#for-bots-using-service-account)