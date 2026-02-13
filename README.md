# PDF Split

> 一个功能强大的PDF分割命令行工具

**PDF Split** 是一个Python CLI工具，支持按页数、范围、书签或关键词分割PDF文件。

## ✨ 功能特性

- 📄 **按固定页数分割** - 将PDF每N页分割为一个文件
- 📌 **按页面范围提取** - 提取指定的页面范围
- 📑 **按书签/章节分割** - 根据PDF书签智能分割
- 🔍 **按关键词分割** - 在关键词出现位置自动分割
- ⚡ **快速高效** - 基于PyMuPDF，处理速度快

## 📦 安装

### 使用 uv 安装

```bash
uv tool install git+https://github.com/MuyaoWorkshop/pdf-split.git
```

### 开发者安装（可编辑模式）

```bash
# 克隆仓库
git clone https://github.com/MuyaoWorkshop/pdf-split.git
cd pdf-split

# 以可编辑模式安装
uv tool install -e .
```

## 🚀 快速开始

### 按固定页数分割

将PDF每10页分割为一个文件：

```bash
pdf-split document.pdf pages 10
```

### 按页面范围提取

提取指定页面范围：

```bash
pdf-split document.pdf range 1-5 8-10
```

### 按书签/章节分割

根据PDF的目录结构自动分割：

```bash
pdf-split ebook.pdf bookmark
```

### 按关键词分割

在每次出现关键词时分割：

```bash
pdf-split document.pdf keyword "Chapter"
```

### 指定输出目录

使用 `-o` 参数指定输出目录：

```bash
pdf-split document.pdf pages 10 -o my_output
```

## 📋 命令参考

```
pdf-split <input.pdf> <mode> [options]

模式:
  pages <num>          按固定页数分割
  range <ranges>        按页面范围提取 (如: 1-5 8-10)
  bookmark             按书签/章节分割
  keyword <word>       按关键词分割

选项:
  -o, --output DIR     输出目录 (默认: output)
  -v, --version        显示版本信息
  -h, --help           显示帮助信息
```

## 🛠️ 作为Python模块使用

```python
from pdf_splitter.splitter import PDFSplitter

# 创建分割器
splitter = PDFSplitter("input.pdf")

# 按页数分割
files = splitter.split_by_pages(10, output_dir="output")

# 按范围提取
files = splitter.split_by_range([(1, 5), (8, 10)], output_dir="output")

# 按书签分割
files = splitter.split_by_bookmark(output_dir="output")

# 按关键词分割
files = splitter.split_by_keyword("Chapter", output_dir="output")
```

## 💡 提示

- **书签分割**：需要PDF包含目录/书签信息
- **关键词分割**：搜索区分大小写
- **输出目录**：会自动创建，如果不存在
- **文件命名**：自动清理特殊字符，避免冲突

## 🔧 项目结构

```
pdf-split/
├── src/
│   └── pdf_splitter/
│       ├── __init__.py    # 包初始化
│       ├── cli.py         # CLI入口点
│       └── splitter.py    # 核心分割逻辑
├── pyproject.toml        # 项目配置
├── README.md             # 项目文档
└── LICENSE               # MIT许可证
```

## 📝 许可证

MIT License - Copyright (c) 2026 muyao

## 🔗 相关链接

- [PyMuPDF文档](https://pymupdf.readthedocs.io/)
- [uv工具文档](https://github.com/astral-sh/uv)

---

**Made with ❤️ by [muyao](https://github.com/MuyaoWorkshop)**
