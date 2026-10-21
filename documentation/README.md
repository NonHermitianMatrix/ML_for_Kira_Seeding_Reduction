# Check repository documentation

This folder checks that a reader can find a guide for every tracked directory and a description for every code file. The check reads Git metadata and guide text. It does not load integral records or model weights.

## Files

- [s00_check_documentation.py](s00_check_documentation.py): checks README coverage and code-file mentions in a chosen Git tree.
- [coverage.json](coverage.json): saved coverage result for the tree recorded by that check.

Run the checker from the repository root:

```bash
python documentation/s00_check_documentation.py --tree HEAD
```

Use `--tree COMMIT` to inspect another commit. Use `--output PATH` to save the result as JSON. The command exits with an error when it finds missing guides or undocumented code files.

A directory link uses the guide at its destination. Files inside archives do not count as Git directories. The check establishes coverage, not the correctness or readability of every explanation; those require review of the guide and its code.
