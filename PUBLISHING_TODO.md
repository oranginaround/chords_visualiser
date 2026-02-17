# PyPI Publishing TODO

## 1) PyPI project setup (required)

- Create or log into your PyPI account: https://pypi.org
- Create a project entry by uploading first release manually OR let GitHub Action publish the first release.
- In PyPI: go to `Account settings -> Publishing` and add a **Trusted Publisher**.

Use these values:
- Owner: `oranginaround`
- Repository: `chords_visualiser`
- Workflow: `.github/workflows/publish-pypi.yml`
- Environment name: `pypi`

Where to put this: configured in **PyPI web UI** (not in repository secrets).

## 2) GitHub environment setup (required)

- In GitHub repo settings: `Settings -> Environments -> New environment`
- Name it exactly: `pypi`
- Optional but recommended protections:
  - Required reviewers
  - Restrict to protected branches/tags

Where to put this: configured in **GitHub repository settings**.

## 3) Release trigger (required)

- Publishing runs automatically when a GitHub Release is published.
- Workflow file location: `.github/workflows/publish-pypi.yml`

## 4) Optional fallback with API token

If you do not want Trusted Publisher yet:
- Create PyPI API token in PyPI (`Account settings -> API tokens`).
- In GitHub repo: `Settings -> Secrets and variables -> Actions -> New repository secret`
- Secret name: `PYPI_API_TOKEN`
- Use local script for manual publish:
  - `PYPI_API_TOKEN=... ./scripts/publish_package.sh`

Where to put this: **GitHub Actions secret** named `PYPI_API_TOKEN`.

## 5) Local tooling prerequisites

- Install `uv`: https://docs.astral.sh/uv/getting-started/installation/
- Build locally:
  - `./scripts/build_package.sh`

## Quick credential checklist

- PyPI account with permission to publish `j6-chords`
- Trusted Publisher registration on PyPI (preferred), OR API token in GitHub secret `PYPI_API_TOKEN`
