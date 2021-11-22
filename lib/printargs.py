from typing import List


def println(num_lines: int = 1):
    for i in range(num_lines):
        print("\n")


def printargs(
    args_list: List[str],
    args_val: List
):
    println()
    for i in range(len(args_list)):
        print(f"{args_list[i]}: {args_val[i]}")
    println()
