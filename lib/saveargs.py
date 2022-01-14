import os
import json

from typing import List
from pathlib import Path


def println(num_lines: int = 1):
    for i in range(num_lines):
        print("\n")


def printargs(args_list: List[str], args_val: List) -> None:
    println()
    for i in range(len(args_list)):
        print(f"{args_list[i]}: {args_val[i]}")
    println()


def saveargs(args_val: List, saveargs_path: Path) -> None:
    args = []
    for i in range(len(args_val)):
        args.append(args_val[i])

    if not os.path.exists(saveargs_path):
        os.makedirs(saveargs_path, exist_ok=True)

    if not os.path.exists(saveargs_path / "executed_args.json"):
        args = [args]
        with open(saveargs_path / "executed_args.json", "w") as f:
            json.dump(args, f)
    else:
        with open(saveargs_path / "executed_args.json", "r") as f:
            old_args = json.load(f)

        old_args.append([args])
        with open(saveargs_path / "executed_args.json", "w") as f:
            json.dump(old_args, f)
