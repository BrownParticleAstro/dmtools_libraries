# DMTools testing

## Automated checks

The API tests target live DMTools. From the repository root, set your DMTools email and enter your API key when prompted.

```zsh
export DMTOOLS_EMAIL='your-email@example.com'
read -rs 'DMTOOLS_API_KEY?DMTools API key: '
export DMTOOLS_API_KEY
```

Replace `19173` with the ID of a data record your account can read. Run the whole folder to include both the API and plot tests. The write tests create their own disposable records and attempt to clean them up.

```zsh
DMTOOLS_TEST_RECORD_ID=19173 MPLBACKEND=Agg .venv/bin/python -m pytest -v testing
```

To check only the plot renderer without API credentials, run this command.

```zsh
MPLBACKEND=Agg .venv/bin/python -m pytest -v testing/test_plot_smoke.py
```
