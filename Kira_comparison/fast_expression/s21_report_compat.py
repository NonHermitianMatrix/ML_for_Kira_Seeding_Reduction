"""Render the frozen report script with the cluster Matplotlib API.

Only two plotting calls need compatibility changes. All numerical calculations,
frozen benchmark sources and the saved results remain unchanged.
"""
from pathlib import Path

SOURCE = Path(__file__).with_name("s14_report.py")


def main():
    source = SOURCE.read_text()
    replacements = [
        (
            'ax.set_yticks(range(len(names)),list(reversed(names)),fontsize=9)',
            'ax.set_yticks(range(len(names)));ax.set_yticklabels(list(reversed(names)),fontsize=9)',
        ),
        (
            'ax.spines[["top","right"]].set_visible(False)',
            'ax.spines["top"].set_visible(False);ax.spines["right"].set_visible(False)',
        ),
    ]
    for old, new in replacements:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    exec(compile(source, str(SOURCE), "exec"),
         {"__name__": "__main__", "__file__": str(SOURCE)})


if __name__ == "__main__":
    main()
