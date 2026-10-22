# mylib

Short one-line description of what mylib does.

This README covers how the package is built and published to PyPI. Publishing is automated: creating a GitHub release builds the package and uploads it to PyPI using [trusted publishing](https://docs.pypi.org/trusted-publishers/), so no API token is stored anywhere.

## How it works

```
GitHub release published
        |
        v
GitHub Actions: build sdist + wheel
        |
        v
GitHub Actions: upload to PyPI (OIDC, environment "pypi")
```

Relevant files:

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package name, version and build config (hatchling) |
| `src/mylib/` | Package source |
| `.github/workflows/publish.yml` | Build and publish pipeline |

## One-time setup

### 1. GitHub environment

Repo > Settings > Environments > New environment, named `pypi`.
Optionally add yourself as a required reviewer so every publish needs approval.

### 2. PyPI trusted publisher

On pypi.org: Account settings > Publishing > Add a new pending publisher.

| Field | Value |
|-------|-------|
| PyPI project name | `mylib` |
| Owner | `YOURUSER` |
| Repository | `mylib` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

These must match GitHub exactly. A "pending" publisher means the project doesn't have to exist on PyPI yet; the first successful run creates it.

### 3. Optional: TestPyPI rehearsal

Repeat step 2 on test.pypi.org, and add `repository-url: https://test.pypi.org/legacy/` to the publish step in the workflow. Remove it once you're happy. A failed upload to TestPyPI costs nothing; on real PyPI a version number is burned once uploaded.

## Check the build locally

```bash
pip install build twine
python -m build
twine check dist/*
```

## Releasing a new version

1. Bump `version` in `pyproject.toml` and commit.
2. Create a release with a matching tag:
   ```bash
   gh release create v0.1.1 --generate-notes
   ```
   Or use GitHub: Releases > Draft a new release > new tag > **Publish release**.
3. Watch the run under the repo's Actions tab. If the `pypi` environment has a required reviewer, approve the deployment.
4. Confirm the new version at https://pypi.org/project/mylib/.

## Troubleshooting

- **`invalid-publisher` error:** the owner, repo, workflow filename or environment name on PyPI doesn't exactly match GitHub.
- **Workflow didn't run:** it only triggers when a release is *published*. Draft releases and bare tag pushes don't trigger it.
- **`File already exists` from PyPI:** that version was already uploaded. PyPI never allows re-uploading a version, even after deletion. Bump the version and release again.
- **Empty wheel or build error:** the folder under `src/` must match the project name (hyphens become underscores).
- **Tag and version out of sync:** the tag isn't linked to `pyproject.toml` by default. Check both match before releasing, or derive the version from the tag with `hatch-vcs`.

## Licence

[MIT](LICENSE)
