"""
Created by Analitika at 02/11/2023
contact@analitika.fr
"""

from pathlib import Path

import typer
from loguru import logger

app = typer.Typer()


class DisplayablePath(object):
    display_filename_prefix_middle = "├──"
    display_filename_prefix_last = "└──"
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(
            [path for path in root.iterdir() if criteria(path)],
            key=lambda s: str(s).lower(),
        )
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(
                    path, parent=displayable_root, is_last=is_last, criteria=criteria
                )
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (
            self.display_filename_prefix_last
            if self.is_last
            else self.display_filename_prefix_middle
        )

        parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                self.display_parent_prefix_middle
                if parent.is_last
                else self.display_parent_prefix_last
            )
            parent = parent.parent

        return "".join(reversed(parts))


def is_not_hidden(this_path):
    return not this_path.name.startswith(".")


def is_not_dunder(this_path):
    if this_path.name == "__init__.py":
        return True  # Exception
    return not this_path.name.startswith("__")


def is_not_excluded(this_path):
    excluded_folders = ["venv", "old"]
    return this_path.name not in excluded_folders


def my_criteria(this_path):
    # not hidden and avoids folders in list
    # remark that there is a _default_criteria that you can modify
    is_not_hidden_ = is_not_hidden(this_path)
    is_not_excluded_ = is_not_excluded(this_path)
    is_not_dunder_ = is_not_dunder(this_path)
    return is_not_hidden_ and is_not_excluded_ and is_not_dunder_


@app.command()
def main():
    # Example usage:
    # With a criteria
    import os
    from datetime import datetime

    exec_time = datetime.today().strftime("%Y-%m-%d %H:%M")
    cpath = Path(__file__).parent.parent

    # Define the file path
    file_path = os.path.join(cpath, "project_structure.txt")
    paths = DisplayablePath.make_tree(Path(cpath), criteria=my_criteria)
    # Open the file in write mode (creates the file if it doesn't exist)
    fullpath = ""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("Created by Analitika: contact@analitika.fr" + "\n")
        file.write(f"Folder PATH listing as of {exec_time}" + "\n")
        file.write("Created with tools.project_tree.DisplayablePath" + "\n\n")
        for path_ in paths:
            file.write(path_.displayable() + "\n")
            fullpath = fullpath + "\n" + path_.displayable()

    logger.success(f"Processing project structure complete:\n{fullpath}")
    logger.info("Printed Tree Structure in ./project_structure.txt...")


if __name__ == "__main__":
    app()
