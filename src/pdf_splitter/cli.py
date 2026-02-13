#!/usr/bin/env python3
"""PDF Splitter CLI - Main entry point"""

import sys
import os
import argparse
from pdf_splitter.splitter import PDFSplitter


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="PDF分割工具 - 支持多种分割模式",
        prog="pdf-split"
    )
    parser.add_argument("input", help="输入PDF文件路径")
    parser.add_argument("-o", "--output", default="output", help="输出目录（默认：output）")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")

    subparsers = parser.add_subparsers(dest="mode", help="分割模式")

    # 按页数分割
    parser_pages = subparsers.add_parser("pages", help="按固定页数分割")
    parser_pages.add_argument("num", type=int, help="每个文件的页数")

    # 按范围分割
    parser_range = subparsers.add_parser("range", help="按页面范围提取")
    parser_range.add_argument("ranges", nargs="+", help="页面范围，如 '1-5 8-10'")

    # 按书签分割
    subparsers.add_parser("bookmark", help="按书签/章节分割")

    # 按关键词分割
    parser_keyword = subparsers.add_parser("keyword", help="按关键词分割")
    parser_keyword.add_argument("keyword", help="分割关键词")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return 0

    if not os.path.exists(args.input):
        print(f"❌ 错误：文件不存在 - {args.input}", file=sys.stderr)
        return 1

    # 创建分割器
    try:
        splitter = PDFSplitter(args.input)

        # 执行分割
        print(f"\n📄 正在处理: {args.input}")
        print(f"📊 总页数: {len(splitter.doc)}\n")

        if args.mode == "pages":
            splitter.split_by_pages(args.num, args.output)

        elif args.mode == "range":
            ranges = []
            for r in args.ranges:
                start, end = map(int, r.split("-"))
                ranges.append((start, end))
            splitter.split_by_range(ranges, args.output)

        elif args.mode == "bookmark":
            splitter.split_by_bookmark(args.output)

        elif args.mode == "keyword":
            splitter.split_by_keyword(args.keyword, args.output)

        print(f"\n✅ 完成！输出目录: {args.output}\n")
        return 0

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
