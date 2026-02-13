"""
PDF分割核心模块
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List, Tuple


class PDFSplitter:
    """PDF分割工具类"""

    def __init__(self, input_pdf: str):
        """
        初始化PDF分割器

        Args:
            input_pdf: 输入PDF文件路径
        """
        self.input_pdf = input_pdf
        self.doc = fitz.open(input_pdf)
        self.filename = Path(input_pdf).stem

    def split_by_pages(self, pages_per_file: int, output_dir: str = "output") -> List[str]:
        """
        按固定页数分割PDF

        Args:
            pages_per_file: 每个文件的页数
            output_dir: 输出目录

        Returns:
            生成的文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        output_files = []

        total_pages = len(self.doc)
        num_files = (total_pages + pages_per_file - 1) // pages_per_file

        for i in range(num_files):
            start_page = i * pages_per_file
            end_page = min((i + 1) * pages_per_file, total_pages)

            # 创建新PDF
            new_doc = fitz.open()
            for page_num in range(start_page, end_page):
                new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)

            # 保存文件（使用优化选项减小文件大小）
            output_path = os.path.join(output_dir, f"{self.filename}_part{i+1}.pdf")
            new_doc.save(
                output_path,
                garbage=4,      # 最彻底的垃圾收集
                deflate=True,    # 压缩流对象
                clean=True,      # 清理未使用的对象
            )
            new_doc.close()
            output_files.append(output_path)

            print(f"✓ 已生成: {output_path} (第{start_page+1}-{end_page}页)")

        self.doc.close()
        return output_files

    def split_by_range(self, page_ranges: List[Tuple[int, int]], output_dir: str = "output") -> List[str]:
        """
        按页面范围提取PDF

        Args:
            page_ranges: 页面范围列表，如 [(1, 5), (8, 10)] 表示提取1-5页和8-10页
            output_dir: 输出目录

        Returns:
            生成的文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        output_files = []

        for idx, (start, end) in enumerate(page_ranges):
            # 转换为0-based索引
            start_page = start - 1
            end_page = min(end, len(self.doc))

            # 创建新PDF
            new_doc = fitz.open()
            for page_num in range(start_page, end_page):
                new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)

            # 保存文件（使用优化选项减小文件大小）
            output_path = os.path.join(output_dir, f"{self.filename}_range_{start}-{end}.pdf")
            new_doc.save(
                output_path,
                garbage=4,
                deflate=True,
                clean=True,
            )
            new_doc.close()
            output_files.append(output_path)

            print(f"✓ 已生成: {output_path} (第{start}-{end}页)")

        self.doc.close()
        return output_files

    def split_by_bookmark(self, output_dir: str = "output") -> List[str]:
        """
        按书签/章节分割PDF

        Args:
            output_dir: 输出目录

        Returns:
            生成的文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        output_files = []

        # 获取书签
        toc = self.doc.get_toc()

        if not toc:
            print("⚠️  该PDF没有书签，无法按书签分割")
            self.doc.close()
            return []

        # 添加最后一个书签指向最后一页
        total_pages = len(self.doc)
        toc.append((toc[-1][0], "End", total_pages))

        # 按书签分割
        for i in range(len(toc) - 1):
            level, title, start_page = toc[i]
            next_level, next_title, end_page = toc[i + 1]

            # 只处理顶级书签（level=1）
            if level == 1:
                # 创建新PDF
                new_doc = fitz.open()
                for page_num in range(start_page - 1, end_page - 1):
                    if page_num < len(self.doc):
                        new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)

                # 清理文件名
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title[:50] if safe_title else f"section_{i+1}"

                # 保存文件（使用优化选项减小文件大小）
                output_path = os.path.join(output_dir, f"{self.filename}_{safe_title}.pdf")
                new_doc.save(
                    output_path,
                    garbage=4,
                    deflate=True,
                    clean=True,
                )
                new_doc.close()
                output_files.append(output_path)

                print(f"✓ 已生成: {output_path} ({title}, 第{start_page}-{end_page-1}页)")

        self.doc.close()
        return output_files

    def split_by_keyword(self, keyword: str, output_dir: str = "output") -> List[str]:
        """
        按关键词分割PDF（在每次出现关键词时分割）

        Args:
            keyword: 分割关键词
            output_dir: 输出目录

        Returns:
            生成的文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        output_files = []

        total_pages = len(self.doc)
        split_points = [0]  # 起始页

        # 搜索关键词
        for page_num in range(total_pages):
            page = self.doc[page_num]
            text = page.get_text()
            if keyword in text:
                split_points.append(page_num)

        split_points.append(total_pages)  # 结束页

        # 分割
        for i in range(len(split_points) - 1):
            start_page = split_points[i]
            end_page = split_points[i + 1]

            if end_page > start_page:
                # 创建新PDF
                new_doc = fitz.open()
                for page_num in range(start_page, end_page):
                    new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)

                # 保存文件（使用优化选项减小文件大小）
                output_path = os.path.join(output_dir, f"{self.filename}_keyword_{i+1}.pdf")
                new_doc.save(
                    output_path,
                    garbage=4,
                    deflate=True,
                    clean=True,
                )
                new_doc.close()
                output_files.append(output_path)

                print(f"✓ 已生成: {output_path} (第{start_page+1}-{end_page}页)")

        self.doc.close()
        return output_files
