# documentation

This folder checks coverage of the folder guides.
Each tracked directory must contain a regular `README.md` file.
A linked directory uses the guide at its link destination.
Archives are files, so their internal paths do not create Git directories.

`s00_check_documentation.py` reads the committed Git tree.
It checks README coverage and code-file mentions.
It does not read integral records or load model weights.
`coverage.json` records the completed check.

Run this command from the project root after publication:

```bash
python documentation/s00_check_documentation.py
```

The guide review used short active sentences and defined technical terms.
Exact commands and identifiers retain their source spelling.
The automated check does not certify every vocabulary choice against the full ASD dictionary.
Earlier README text remains in Git history.

## Code files

The entries below follow file-name order.
Each entry gives its purpose and the input or output interface available in the source.

[s00_check_documentation.py](s00_check_documentation.py)

The program checks folder-guide coverage without loading scientific data or model weights.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

ROOT = Path(__file__).resolve().parents[1]

```

The command accepts these parser options:

- `'--tree'`: default='HEAD'; help='Git tree or commit to inspect.'.
- `'--output'`: type=Path; help='Optional JSON output file.'.

These calls show the stored input and output interface:

```python

args.output.write_text(json.dumps(result, indent=2) + '\n')

```

## Data and supporting files

- [coverage.json](coverage.json): This file records folder and code documentation coverage.
