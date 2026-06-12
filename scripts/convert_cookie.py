#!/usr/bin/env python3
"""Cookie format converter.

Converts between two cookie JSON formats:
  - dict:  {"key": "value", ...}
  - list:  [{"name": "key", "value": "value"}, ...]
"""

import argparse
import json
import sys


def detect_format(data: list | dict) -> str:
    if isinstance(data, dict):
        return "dict"
    if isinstance(data, list):
        if len(data) == 0 or (isinstance(data[0], dict) and "name" in data[0]):
            return "list"
    raise ValueError("无法识别的 Cookie 格式")


def dict_to_list(data: dict) -> list[dict]:
    return [{"name": k, "value": v} for k, v in data.items()]


def list_to_dict(data: list[dict]) -> dict:
    return {item["name"]: item["value"] for item in data}


def convert(
    data: list | dict, input_fmt: str | None, output_fmt: str | None
) -> list | dict:
    detected = detect_format(data)
    src = input_fmt or detected

    if src == "dict":
        if not isinstance(data, dict):
            raise ValueError(f"指定了 dict 格式，但输入是 {type(data).__name__}")
        dst = output_fmt or "list"
        if dst == "list":
            return dict_to_list(data)
        return data  # dict -> dict，原样输出

    if src == "list":
        if not isinstance(data, list):
            raise ValueError(f"指定了 list 格式，但输入是 {type(data).__name__}")
        dst = output_fmt or "dict"
        if dst == "dict":
            return list_to_dict(data)
        return data  # list -> list，原样输出

    raise ValueError(f"未知格式: {src}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="在 dict 格式和 list 格式之间转换 Cookie JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从文件读取，自动检测格式
  python convert_cookie.py cookies.json

  # 从 stdin 读取
  cat cookies.json | python convert_cookie.py

  # 指定输入/输出格式
  python convert_cookie.py -i list -o dict cookies.json

  # 格式化输出
  python convert_cookie.py --pretty cookies.json
""",
    )
    parser.add_argument("file", nargs="?", help="输入文件（不指定则从 stdin 读取）")
    parser.add_argument(
        "-i",
        "--input-format",
        choices=["dict", "list"],
        dest="input_fmt",
        help="指定输入格式（默认自动检测）",
    )
    parser.add_argument(
        "-o",
        "--output-format",
        choices=["dict", "list"],
        dest="output_fmt",
        help="指定输出格式（默认与输入相反）",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="格式化输出（默认紧凑输出）",
    )

    args = parser.parse_args()

    # 读取输入
    try:
        if args.file:
            with open(args.file, encoding="utf-8") as f:
                raw = f.read()
        else:
            raw = sys.stdin.read()
    except FileNotFoundError:
        print(f"错误:找不到文件 {args.file!r}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"错误: 读取文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 解析 JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 转换
    try:
        result = convert(data, args.input_fmt, args.output_fmt)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
