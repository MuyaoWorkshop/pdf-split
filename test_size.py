#!/usr/bin/env python3
"""
测试PDF文件大小优化效果
"""

import fitz
import os


def create_test_pdf():
    """创建一个测试PDF"""
    doc = fitz.open()

    # 创建20页测试PDF
    for i in range(20):
        page = doc.new_page(width=595, height=842)  # A4
        text = f"这是第 {i+1} 页的测试内容\n" * 10
        page.insert_text(fitz.Point(50, 100), text, fontsize=12)

    doc.save("test_original.pdf")
    doc.close()

    return os.path.getsize("test_original.pdf")


def split_with_optimization():
    """使用优化方式分割"""
    from pdf_splitter.splitter import PDFSplitter

    splitter = PDFSplitter("test_original.pdf")
    files = splitter.split_by_pages(5, output_dir="output_optimized")

    sizes = {}
    for f in files:
        sizes[f] = os.path.getsize(f)

    return sizes


def format_size(bytes_size):
    """格式化文件大小"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


if __name__ == "__main__":
    print("=" * 60)
    print("PDF分割文件大小测试")
    print("=" * 60)

    # 创建测试PDF
    print("\n1. 创建测试PDF...")
    original_size = create_test_pdf()
    print(f"   原始文件大小: {format_size(original_size)}")

    # 使用优化方式分割
    print("\n2. 使用优化方式分割...")
    optimized_sizes = split_with_optimization()

    print("\n3. 结果分析:")
    print("-" * 60)
    total_output_size = sum(optimized_sizes.values())

    for filename, size in optimized_sizes.items():
        print(f"   {filename:40} {format_size(size):>10}")

    print("-" * 60)
    print(f"   总大小: {format_size(total_output_size):>51}")
    print(f"   原始大小: {format_size(original_size):>51}")
    print(f"   增长: {format_size(total_output_size - original_size):>51}")
    print(f"   增长率: {(total_output_size / original_size - 1) * 100:.1f}%")

    print("\n💡 说明:")
    print("   - 优化后的文件应该比未优化版本小很多")
    print("   - 文件增大主要是因为字体和资源的重复嵌入")
    print("   - garbage=4 清理未使用的对象")
    print("   - deflate=True 压缩流对象")
    print("   - clean=True 清理未使用的资源")
