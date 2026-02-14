"""
PDF分割核心模块
"""

import pymupdf  # PyMuPDF
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
        self.doc = pymupdf.open(input_pdf)
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
            new_doc = pymupdf.open()
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
            new_doc = pymupdf.open()
            page_count = 0
            for page_num in range(start_page, end_page):
                new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)
                page_count += 1

            # 只有当新PDF有页面时才保存
            if page_count > 0:
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
            else:
                # 跳过空PDF并关闭文档
                new_doc.close()
                print(f"⚠️  跳过空范围: 第{start}-{end}页，无页面")

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

            # 只处理顶级书签（level=1）
            if level == 1:
                # 找下一个level=1的书签作为结束点
                end_page = None
                for j in range(i + 1, len(toc)):
                    if toc[j][0] == 1:  # level=1
                        end_page = toc[j][2]
                        break

                # 如果没找到下一个level=1的书签，使用文档末尾
                if end_page is None:
                    end_page = len(self.doc) + 1  # +1因为要转换为0-based

                # 创建新PDF
                new_doc = pymupdf.open()
                page_count = 0

                # 转换为0-based索引并复制页面
                for page_num in range(start_page - 1, end_page - 1):
                    if page_num < len(self.doc):
                        new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)
                        page_count += 1

                # 收集并设置书签到新PDF
                # 收集这个章节的书签（包括当前level=1和其子level=2的书签）
                section_toc = [(level, title, 1)]  # 第1页开始
                for j in range(i + 1, len(toc)):
                    sub_level, sub_title, sub_page = toc[j]
                    # 添加子章节直到下一个level=1的书签
                    if sub_level == 1:
                        break
                    if sub_page < end_page:
                        # 计算相对于新文档的页码
                        relative_page = sub_page - start_page + 1
                        section_toc.append((sub_level, sub_title, relative_page))

                # 设置书签到新PDF（只在有页面且有书签时）
                if page_count > 0 and len(section_toc) > 1:
                    new_doc.set_toc(section_toc)

                # 只有当新PDF有页面时才保存
                if page_count > 0:
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

                    # 计算实际复制的最后一页（转换为1-based）
                    last_page_copied = start_page + page_count - 1
                    print(f"✓ 已生成: {output_path} ({title}, 第{start_page}-{last_page_copied}页)")
                else:
                    # 跳过空PDF并关闭文档
                    new_doc.close()
                    print(f"⚠️  跳过空书签: {title} (第{start_page}页)")

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
                new_doc = pymupdf.open()
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
