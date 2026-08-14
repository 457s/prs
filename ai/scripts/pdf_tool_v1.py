"""
专业PDF编辑工具 v3.1
========================
功能特性：
  1. ✂️  拆分PDF       - 每页拆分为独立文件 / 按范围拆分
  2. 🔄  旋转页面       - 90°/180°/270°，支持全部/指定页/奇数页/偶数页
  3. 📋  提取页面       - 按页码范围/奇数页/偶数页提取为新PDF
  4. 🗑️  删除页面       - 删除指定页/奇数页/偶数页
  5. 📄  插入空白页     - 在指定位置插入空白页，可选多种纸张尺寸
  6. 🔐  加密/解密      - 设置/移除PDF密码，支持权限控制
  7. 💧  添加水印       - 文字水印（透明度/角度/字体/颜色/范围）
  8. 📏  裁剪页面       - 自定义四边裁剪或预设方案，支持奇偶页
  9. 🔀  页面排序       - 自定义顺序/倒序/偶数页在前/奇数页在前
 10. 🏷️  编辑元数据     - 查看/修改标题、作者、主题、关键词等
 11. 🔗  合并PDF        - 多文件按序合并
 12. 🖼️  页面缩放       - 按比例缩放PDF页面内容，支持奇偶页
 13. 📊  信息统计       - 查看PDF页数、版本、加密状态等

核心设计：
  - 输出文件默认路径 = 输入文件所在目录（无需手动选择保存位置）
  - 输出文件若已存在自动添加 _1 _2 后缀，绝不覆盖
  - 基于 pypdf 高效处理，界面使用 tkinter (内置)
  - 水印功能需要额外安装 reportlab

依赖安装（任选其一）：
  pip install pypdf
  pip install reportlab   # 仅水印功能需要
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions


# ============================================================
#  工具函数
# ============================================================

def parse_page_range(range_str: str, total_pages: int) -> list:
    """解析页码字符串，返回0-based页码列表
    支持:
      - 单页: 1,3,5
      - 范围: 1-5
      - 混合: 1,3-5,7
      - ODD  -> 所有奇数页 (1,3,5,...)
      - EVEN -> 所有偶数页 (2,4,6,...)
    """
    s = range_str.strip().upper()
    if s == "ODD":
        return [i for i in range(total_pages) if (i + 1) % 2 == 1]
    if s == "EVEN":
        return [i for i in range(total_pages) if (i + 1) % 2 == 0]
    if not s:
        return list(range(total_pages))
    pages = []
    for part in range_str.split(","):
        part = part.strip().upper()
        if not part:
            continue
        if part == "ODD":
            pages.extend(i for i in range(total_pages) if (i + 1) % 2 == 1)
        elif part == "EVEN":
            pages.extend(i for i in range(total_pages) if (i + 1) % 2 == 0)
        elif "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str.strip()) - 1
            end = int(end_str.strip()) - 1
            if start < 0:
                start = 0
            if end >= total_pages:
                end = total_pages - 1
            if start <= end:
                pages.extend(range(start, end + 1))
        else:
            p = int(part) - 1
            if 0 <= p < total_pages:
                pages.append(p)
    return sorted(set(pages))


def safe_int(value, default=0):
    """安全转换int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=1.0):
    """安全转换float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_unique_path(path: str) -> str:
    """如果文件已存在，自动添加后缀 _1 _2 ... 确保不覆盖"""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    counter = 1
    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def parse_page_range_ordered(range_str: str, total_pages: int) -> list:
    """解析页码字符串，返回0-based页码列表（保留输入顺序，用于页面排序）
    支持:
      - 单页: 1,3,5
      - 范围: 1-5
      - 混合: 1,3-5,7
      注意: 不排序、不去重，保留用户输入的先后顺序
    """
    s = range_str.strip().upper()
    if not s:
        return list(range(total_pages))
    pages = []
    seen = set()
    for part in range_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str.strip()) - 1
            end = int(end_str.strip()) - 1
            if start < 0:
                start = 0
            if end >= total_pages:
                end = total_pages - 1
            if start <= end:
                for i in range(start, end + 1):
                    if i not in seen:
                        pages.append(i)
                        seen.add(i)
        else:
            p = int(part) - 1
            if 0 <= p < total_pages and p not in seen:
                pages.append(p)
                seen.add(p)
    return pages


def get_file_info(path: str) -> str:
    """获取PDF文件基本信息"""
    try:
        reader = PdfReader(path)
        pages = len(reader.pages)
        encrypted = reader.is_encrypted
        info_parts = [f"📄 共 {pages} 页"]
        if encrypted:
            info_parts.append("🔒 已加密")
        try:
            ver = reader.pdf_header
            if ver:
                info_parts.append(f"v{ver}")
        except Exception:
            pass
        return " | ".join(info_parts)
    except Exception as e:
        return f"⚠️ 读取失败: {str(e)}"


# ============================================================
#  标签页基类 - 提供公共UI逻辑
# ============================================================

class BaseTab:
    """所有功能标签页的基类"""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        raise NotImplementedError

    def add_log_area(self, parent):
        """添加日志显示区域（默认隐藏）"""
        self.log_label = ttk.Label(parent, text="", font=("微软雅黑", 9),
                                   wraplength=600, justify=tk.LEFT)
        return self.log_label

    def log(self, text, color="#2d3436"):
        """在界面打印日志"""
        self.log_label.config(text=text, foreground=color)
        self.log_label.pack(anchor=tk.W, pady=2, before=self._action_btn)
        self.app.root.update_idletasks()

    def log_running(self, msg="正在执行..."):
        """打印执行中"""
        self.log(f"⏳ {msg}", "#0984e3")

    def log_success(self, msg):
        """打印执行成功"""
        self.log(f"✅ 执行完毕 | {msg}", "#00b894")

    def log_error(self, msg):
        """打印错误"""
        self.log(f"⏳ 正在执行... ↓\n❌ {msg}", "#d63031")

    def add_odd_even_buttons(self, parent, entry_widget):
        """添加 奇数页/偶数页 快捷按钮"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text="快捷:").pack(side=tk.LEFT)
        ttk.Button(frame, text="仅奇数页",
                   command=lambda: self._set_entry(entry_widget, "ODD")).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="仅偶数页",
                   command=lambda: self._set_entry(entry_widget, "EVEN")).pack(side=tk.LEFT, padx=2)
        return frame

    def _set_entry(self, entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    # ---------- 文件选择组件（核心：自动设置输出路径） ----------

    def add_file_selector(self, parent, label, key,
                          auto_output_entry=None, auto_out_name=None):
        """添加文件选择行
        若提供 auto_output_entry 和 auto_out_name，选择文件后自动将输出路径设为同目录
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)
        ttk.Label(frame, text=label, width=8).pack(side=tk.LEFT)
        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        btn = ttk.Button(frame, text="📂 浏览", width=8,
                         command=lambda: self._browse_file(
                             entry, key, auto_output_entry, auto_out_name))
        btn.pack(side=tk.LEFT)

        # 文件信息标签
        info_label = ttk.Label(parent, text="", foreground="#636e72")
        info_label.pack(anchor=tk.W, padx=78, pady=1)
        setattr(self, f"{key}_info", info_label)
        return entry, info_label

    def _browse_file(self, entry, key, auto_output_entry=None, auto_out_name=None):
        path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if not path:
            return
        entry.delete(0, tk.END)
        entry.insert(0, path)

        # 更新文件信息
        info_label = getattr(self, f"{key}_info", None)
        if info_label:
            info_label.config(text=get_file_info(path))

        # ★ 核心功能：自动设置输出路径为源文件同目录
        if auto_output_entry and auto_out_name:
            src_dir = os.path.dirname(path)
            auto_output_entry.delete(0, tk.END)
            auto_output_entry.insert(0, os.path.join(src_dir, auto_out_name))

    # ---------- 输出选择组件 ----------

    def add_output_selector(self, parent, label, key, default_name="output.pdf"):
        """添加输出文件选择行，返回entry_widget"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)
        ttk.Label(frame, text=label, width=10).pack(side=tk.LEFT)
        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        entry.insert(0, default_name)
        btn = ttk.Button(frame, text="📁 另存为", width=10,
                         command=lambda: self._save_file(entry))
        btn.pack(side=tk.LEFT)
        return entry

    def add_output_dir_selector(self, parent, label, key, default_dir=""):
        """添加输出目录选择行，返回entry_widget"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)
        ttk.Label(frame, text=label, width=10).pack(side=tk.LEFT)
        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        if default_dir:
            entry.insert(0, default_dir)
        btn = ttk.Button(frame, text="📁 选择目录", width=10,
                         command=lambda: self._choose_dir(entry))
        btn.pack(side=tk.LEFT)
        return entry

    # ---------- 辅助方法 ----------

    def _choose_dir(self, entry):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def _save_file(self, entry):
        path = filedialog.asksaveasfilename(
            title="保存PDF",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def add_separator(self, parent):
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

    def add_title(self, parent, text):
        ttk.Label(parent, text=text,
                  font=("微软雅黑", 10, "bold")).pack(anchor=tk.W)

    def add_action_button(self, parent, text, command):
        btn = ttk.Button(parent, text=text, command=command,
                         style="Accent.TButton")
        btn.pack(pady=8)
        self._action_btn = btn
        return btn

    def add_info_label(self, parent, text="", color="#636e72"):
        lbl = ttk.Label(parent, text=text, foreground=color)
        lbl.pack(anchor=tk.W, pady=2)
        return lbl


# ============================================================
#  各功能标签页实现
# ============================================================

# ---------- 1. 拆分PDF ----------

class SplitTab(BaseTab):
    """拆分PDF：每页拆分为独立文件"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "✂️ 将PDF的每一页拆分为单独的PDF文件")
        self.add_separator(frame)

        self.src_entry, self.src_info = self.add_file_selector(
            frame, "源文件:", "split")

        self.out_dir_entry = self.add_output_dir_selector(
            frame, "输出到:", "split_dir")

        self.src_entry.bind("<KeyRelease>", self._auto_set_outdir)

        pref_frame = ttk.Frame(frame)
        pref_frame.pack(fill=tk.X, pady=3)
        ttk.Label(pref_frame, text="文件名前缀:", width=10).pack(side=tk.LEFT)
        self.prefix_entry = ttk.Entry(pref_frame, width=20)
        self.prefix_entry.pack(side=tk.LEFT, padx=4)
        self.prefix_entry.insert(0, "page_")

        mode_frame = ttk.LabelFrame(frame, text="拆分模式", padding=8)
        mode_frame.pack(fill=tk.X, pady=6)
        self.split_mode = tk.StringVar(value="all")
        ttk.Radiobutton(mode_frame, text="每页一个文件（全部拆分）",
                        variable=self.split_mode, value="all",
                        command=self._toggle_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="按范围分组拆分",
                        variable=self.split_mode, value="range",
                        command=self._toggle_mode).pack(anchor=tk.W)
        range_frame = ttk.Frame(mode_frame)
        range_frame.pack(fill=tk.X, pady=4)
        ttk.Label(range_frame, text="每组合并页数:").pack(side=tk.LEFT)
        self.group_size = ttk.Spinbox(range_frame, from_=2, to=50, width=8)
        self.group_size.set(5)
        self.group_size.pack(side=tk.LEFT, padx=4)
        self.group_size.config(state="disabled")

        self.add_log_area(frame)
        self.add_action_button(frame, "✂️ 开始拆分", self.split_pdf)

    def _toggle_mode(self):
        state = "normal" if self.split_mode.get() == "range" else "disabled"
        self.group_size.config(state=state)

    def _auto_set_outdir(self, event=None):
        src = self.src_entry.get().strip()
        if src and os.path.isfile(src):
            src_dir = os.path.dirname(src)
            self.out_dir_entry.delete(0, tk.END)
            self.out_dir_entry.insert(0, src_dir)

    def split_pdf(self):
        self.log_running("正在拆分...")
        src = self.src_entry.get().strip()
        out_dir = self.out_dir_entry.get().strip()
        prefix = self.prefix_entry.get().strip() or "page_"

        if not src:
            self.log_error("请选择要拆分的PDF文件")
            return
        if not out_dir:
            self.log_error("请选择输出目录")
            return
        os.makedirs(out_dir, exist_ok=True)

        try:
            reader = PdfReader(src)
            base_name = os.path.splitext(os.path.basename(src))[0]
            total = len(reader.pages)
            mode = self.split_mode.get()

            if mode == "all":
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    filename = f"{prefix}{base_name}_p{i+1:03d}.pdf"
                    out_path = get_unique_path(os.path.join(out_dir, filename))
                    with open(out_path, "wb") as f:
                        writer.write(f)
                self.log_success(f"拆分 {total} 页 → {total} 个文件")
            else:
                group_n = safe_int(self.group_size.get(), 5)
                if group_n < 2:
                    group_n = 2
                group_idx = 0
                for start in range(0, total, group_n):
                    end = min(start + group_n, total)
                    writer = PdfWriter()
                    for i in range(start, end):
                        writer.add_page(reader.pages[i])
                    filename = f"{prefix}{base_name}_group{group_idx+1:02d}.pdf"
                    out_path = get_unique_path(os.path.join(out_dir, filename))
                    with open(out_path, "wb") as f:
                        writer.write(f)
                    group_idx += 1
                self.log_success(f"拆分 {total} 页 → {group_idx} 个分组文件")
        except Exception as e:
            self.log_error(f"拆分失败: {str(e)}")


# ---------- 2. 旋转页面 ----------

class RotateTab(BaseTab):
    """旋转页面"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "🔄 旋转PDF中的页面")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "rotate_out",
                                                  default_name="旋转后.pdf")
        self.src_entry, self.src_info = self.add_file_selector(
            frame, "源文件:", "rotate",
            auto_output_entry=self.out_entry, auto_out_name="旋转后.pdf")

        opt_frame = ttk.LabelFrame(frame, text="旋转设置", padding=8)
        opt_frame.pack(fill=tk.X, pady=6)

        self.rotate_angle = tk.StringVar(value="90")
        ttk.Radiobutton(opt_frame, text="顺时针 90°",
                        variable=self.rotate_angle, value="90").pack(anchor=tk.W)
        ttk.Radiobutton(opt_frame, text="逆时针 90° (270°)",
                        variable=self.rotate_angle, value="270").pack(anchor=tk.W)
        ttk.Radiobutton(opt_frame, text="旋转 180°",
                        variable=self.rotate_angle, value="180").pack(anchor=tk.W)

        range_frame = ttk.LabelFrame(opt_frame, text="应用范围", padding=5)
        range_frame.pack(fill=tk.X, pady=4)

        self.rotate_range = tk.StringVar(value="all")
        ttk.Radiobutton(range_frame, text="所有页面",
                        variable=self.rotate_range, value="all",
                        command=self._toggle_range).pack(anchor=tk.W)
        ttk.Radiobutton(range_frame, text="仅奇数页",
                        variable=self.rotate_range, value="odd",
                        command=self._toggle_range).pack(anchor=tk.W)
        ttk.Radiobutton(range_frame, text="仅偶数页",
                        variable=self.rotate_range, value="even",
                        command=self._toggle_range).pack(anchor=tk.W)
        ttk.Radiobutton(range_frame, text="指定页面",
                        variable=self.rotate_range, value="custom",
                        command=self._toggle_range).pack(anchor=tk.W)

        page_frame = ttk.Frame(range_frame)
        page_frame.pack(fill=tk.X, pady=2)
        ttk.Label(page_frame, text="页码(如 1,3-5):").pack(side=tk.LEFT)
        self.rotate_pages_entry = ttk.Entry(page_frame)
        self.rotate_pages_entry.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        self.rotate_pages_entry.config(state="disabled")

        self.add_log_area(frame)
        self.add_action_button(frame, "🔄 开始旋转", self.rotate_pdf)

    def _toggle_range(self):
        state = "normal" if self.rotate_range.get() == "custom" else "disabled"
        self.rotate_pages_entry.config(state=state)

    def _get_target_pages(self, total):
        mode = self.rotate_range.get()
        if mode == "all":
            return list(range(total))
        elif mode == "odd":
            return [i for i in range(total) if (i + 1) % 2 == 1]
        elif mode == "even":
            return [i for i in range(total) if (i + 1) % 2 == 0]
        else:
            pages_str = self.rotate_pages_entry.get().strip()
            if not pages_str:
                return None
            try:
                return [int(p.strip()) - 1 for p in pages_str.split(",")]
            except ValueError:
                return None

    def rotate_pdf(self):
        self.log_running("正在旋转...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()
        angle = int(self.rotate_angle.get())

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return

        try:
            reader = PdfReader(src)
            writer = PdfWriter()
            total = len(reader.pages)

            mode = self.rotate_range.get()
            if mode == "custom":
                pages_raw = self._get_target_pages(total)
                if pages_raw is None:
                    self.log_error("请输入要旋转的页码")
                    return
                target_set = set(pages_raw)
            else:
                pages_raw = self._get_target_pages(total)
                target_set = set(pages_raw)  # type: ignore[arg-type]

            for i, page in enumerate(reader.pages):
                if i in target_set:
                    page.rotate(angle)
                writer.add_page(page)

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)
            self.log_success(f"旋转完成 → {os.path.basename(out)}")
        except Exception as e:
            self.log_error(f"旋转失败: {str(e)}")


# ---------- 3. 提取页面 ----------

class ExtractTab(BaseTab):
    """提取页面"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "📋 从PDF中提取指定页面保存为新PDF")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "extract_out",
                                                  default_name="提取结果.pdf")
        self.src_entry, self.src_info = self.add_file_selector(
            frame, "源文件:", "extract",
            auto_output_entry=self.out_entry, auto_out_name="提取结果.pdf")

        opt_frame = ttk.LabelFrame(frame, text="提取设置", padding=8)
        opt_frame.pack(fill=tk.X, pady=6)

        ttk.Label(opt_frame, text="支持格式:\n• 单页: 1,3,5\n• 范围: 1-5\n• 混合: 1,3-5,7\n• 关键字: ODD(奇数页), EVEN(偶数页)",
                  foreground="#555").pack(anchor=tk.W)
        range_frame = ttk.Frame(opt_frame)
        range_frame.pack(fill=tk.X, pady=4)
        ttk.Label(range_frame, text="页码范围:").pack(side=tk.LEFT)
        self.range_entry = ttk.Entry(range_frame)
        self.range_entry.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        self.add_odd_even_buttons(opt_frame, self.range_entry)

        self.add_log_area(frame)
        self.add_action_button(frame, "📋 开始提取", self.extract_pages)

    def extract_pages(self):
        self.log_running("正在提取...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()
        range_str = self.range_entry.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return
        if not range_str:
            self.log_error("请输入要提取的页码范围")
            return

        try:
            reader = PdfReader(src)
            total = len(reader.pages)
            pages = parse_page_range(range_str, total)
            if not pages:
                self.log_error("未找到有效的页码")
                return

            writer = PdfWriter()
            for p in pages:
                writer.add_page(reader.pages[p])

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)
            self.log_success(f"提取 {len(pages)} 页 → {os.path.basename(out)}")
        except Exception as e:
            self.log_error(f"提取失败: {str(e)}")


# ---------- 4. 删除页面 ----------

class DeletePagesTab(BaseTab):
    """删除页面"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "🗑️ 从PDF中删除指定页面")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "delete_out",
                                                  default_name="删除后.pdf")
        self.src_entry, self.src_info = self.add_file_selector(
            frame, "源文件:", "delete",
            auto_output_entry=self.out_entry, auto_out_name="删除后.pdf")

        opt_frame = ttk.LabelFrame(frame, text="删除设置", padding=8)
        opt_frame.pack(fill=tk.X, pady=6)
        ttk.Label(opt_frame, text="支持格式:\n• 单页: 1,3,5\n• 范围: 1-5\n• 关键字: ODD(奇数页), EVEN(偶数页)",
                  foreground="#555").pack(anchor=tk.W)
        range_frame = ttk.Frame(opt_frame)
        range_frame.pack(fill=tk.X, pady=4)
        ttk.Label(range_frame, text="要删除的页:").pack(side=tk.LEFT)
        self.del_entry = ttk.Entry(range_frame)
        self.del_entry.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        self.add_odd_even_buttons(opt_frame, self.del_entry)

        self.add_log_area(frame)
        self.add_action_button(frame, "🗑️ 删除页面", self.delete_pages)

    def delete_pages(self):
        self.log_running("正在删除...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()
        range_str = self.del_entry.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return
        if not range_str:
            self.log_error("请输入要删除的页码范围")
            return

        try:
            reader = PdfReader(src)
            total = len(reader.pages)
            del_pages = set(parse_page_range(range_str, total))
            if not del_pages:
                self.log_error("未找到有效的页码")
                return

            writer = PdfWriter()
            for i, page in enumerate(reader.pages):
                if i not in del_pages:
                    writer.add_page(page)

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)
            remaining = total - len(del_pages)
            self.log_success(f"删除 {len(del_pages)} 页，剩余 {remaining} 页")
        except Exception as e:
            self.log_error(f"删除失败: {str(e)}")


# ---------- 5. 插入空白页 ----------

class InsertBlankTab(BaseTab):
    """插入空白页"""

    SIZE_MAP = {
        "A4":          (595.28, 841.89),
        "A3":          (841.89, 1190.55),
        "A5":          (420.94, 595.28),
        "Letter":      (612.0,  792.0),
        "Legal":       (612.0,  1008.0),
        "Tabloid":     (792.0,  1224.0),
    }

    def _build(self):
        frame = self.frame
        self.add_title(frame, "📄 在PDF中插入空白页面")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "insert_out",
                                                  default_name="插入后.pdf")
        self.src_entry, self.src_info = self.add_file_selector(
            frame, "源文件:", "insert",
            auto_output_entry=self.out_entry, auto_out_name="插入后.pdf")

        opt_frame = ttk.LabelFrame(frame, text="插入设置", padding=8)
        opt_frame.pack(fill=tk.X, pady=6)

        pos_frame = ttk.Frame(opt_frame)
        pos_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pos_frame, text="插入位置:").pack(side=tk.LEFT)
        self.insert_pos = ttk.Combobox(pos_frame,
                                       values=["在开头", "在结尾",
                                               "在每一页之前", "在每一页之后",
                                               "在指定页之前", "在指定页之后",
                                               "在奇数页之后", "在偶数页之后"],
                                       state="readonly", width=17)
        self.insert_pos.current(0)
        self.insert_pos.pack(side=tk.LEFT, padx=4)
        self.insert_pos.bind("<<ComboboxSelected>>", self._toggle_page_input)

        self.insert_page_num = ttk.Entry(opt_frame, width=10)
        self.insert_page_num.insert(0, "1")
        self.insert_page_num.pack(anchor=tk.W, padx=10, pady=2)
        self.insert_page_num.config(state="disabled")
        ttk.Label(opt_frame, text="页码(仅'指定页'模式有效)",
                  foreground="#888").pack(anchor=tk.W, padx=10)

        count_frame = ttk.Frame(opt_frame)
        count_frame.pack(fill=tk.X, pady=2)
        ttk.Label(count_frame, text="插入页数:").pack(side=tk.LEFT)
        self.insert_count = ttk.Spinbox(count_frame, from_=1, to=100, width=8)
        self.insert_count.set(1)
        self.insert_count.pack(side=tk.LEFT, padx=4)

        size_orient_frame = ttk.Frame(opt_frame)
        size_orient_frame.pack(fill=tk.X, pady=2)
        ttk.Label(size_orient_frame, text="纸张大小:").pack(side=tk.LEFT)
        self.page_size = ttk.Combobox(size_orient_frame,
                                      values=list(self.SIZE_MAP.keys()),
                                      state="readonly", width=10)
        self.page_size.current(0)
        self.page_size.pack(side=tk.LEFT, padx=4)
        ttk.Label(size_orient_frame, text="方向:").pack(side=tk.LEFT, padx=(10,0))
        self.orientation = ttk.Combobox(size_orient_frame,
                                        values=["纵向", "横向"],
                                        state="readonly", width=6)
        self.orientation.current(0)
        self.orientation.pack(side=tk.LEFT, padx=4)

        self.add_log_area(frame)
        self.add_action_button(frame, "📄 插入空白页", self.insert_blank)

    def _toggle_page_input(self, event=None):
        pos = self.insert_pos.get()
        state = "normal" if "指定页" in pos else "disabled"
        self.insert_page_num.config(state=state)

    def _get_page_size(self):
        pw, ph = self.SIZE_MAP.get(self.page_size.get(), (595.28, 841.89))
        orient = self.orientation.get()
        if orient == "横向":
            pw, ph = ph, pw
        return pw, ph

    def insert_blank(self):
        self.log_running("正在插入...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return

        try:
            reader = PdfReader(src)
            writer = PdfWriter()
            total = len(reader.pages)
            position = self.insert_pos.get()
            count = max(1, safe_int(self.insert_count.get(), 1))
            pw, ph = self._get_page_size()
            existing_pages = list(reader.pages)

            if position == "在开头":
                for _ in range(count):
                    writer.add_blank_page(pw, ph)
                for p in existing_pages:
                    writer.add_page(p)
            elif position == "在结尾":
                for p in existing_pages:
                    writer.add_page(p)
                for _ in range(count):
                    writer.add_blank_page(pw, ph)
            elif position == "在每一页之前":
                for p in existing_pages:
                    for _ in range(count):
                        writer.add_blank_page(pw, ph)
                    writer.add_page(p)
            elif position == "在每一页之后":
                for p in existing_pages:
                    writer.add_page(p)
                    for _ in range(count):
                        writer.add_blank_page(pw, ph)
            elif position == "在指定页之前":
                pos = max(0, min(total, safe_int(self.insert_page_num.get(), 1) - 1))
                for i, p in enumerate(existing_pages):
                    if i == pos:
                        for _ in range(count):
                            writer.add_blank_page(pw, ph)
                    writer.add_page(p)
            elif position == "在指定页之后":
                pos = max(1, min(total, safe_int(self.insert_page_num.get(), 1)))
                for i, p in enumerate(existing_pages):
                    writer.add_page(p)
                    if i == pos - 1:
                        for _ in range(count):
                            writer.add_blank_page(pw, ph)
            elif position == "在奇数页之后":
                for i, p in enumerate(existing_pages):
                    writer.add_page(p)
                    if (i + 1) % 2 == 1:
                        for _ in range(count):
                            writer.add_blank_page(pw, ph)
            elif position == "在偶数页之后":
                for i, p in enumerate(existing_pages):
                    writer.add_page(p)
                    if (i + 1) % 2 == 0:
                        for _ in range(count):
                            writer.add_blank_page(pw, ph)

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)

            if position in ("在每一页之前", "在每一页之后"):
                new_total = total * (1 + count)
            elif "奇数" in position:
                odd_count = (total + 1) // 2
                new_total = total + odd_count * count
            elif "偶数" in position:
                even_count = total // 2
                new_total = total + even_count * count
            else:
                new_total = total + count

            orient_text = self.orientation.get()
            self.log_success(f"原 {total} 页 → {new_total} 页 ({self.page_size.get()} {orient_text})")
        except Exception as e:
            self.log_error(f"插入失败: {str(e)}")


# ---------- 6. 加密/解密 ----------

class EncryptTab(BaseTab):
    """加密/解密PDF"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "🔐 为PDF设置或移除密码保护")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "encrypt_out",
                                                  default_name="加密后.pdf")
        self.src_entry, _ = self.add_file_selector(
            frame, "源文件:", "encrypt",
            auto_output_entry=self.out_entry, auto_out_name="加密后.pdf")

        mode_frame = ttk.LabelFrame(frame, text="操作模式", padding=8)
        mode_frame.pack(fill=tk.X, pady=6)

        self.encrypt_mode = tk.StringVar(value="encrypt")
        ttk.Radiobutton(mode_frame, text="🔐 加密PDF（设置密码）",
                        variable=self.encrypt_mode, value="encrypt",
                        command=self._toggle_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="🔓 解密PDF（移除密码）",
                        variable=self.encrypt_mode, value="decrypt",
                        command=self._toggle_mode).pack(anchor=tk.W)

        pwd_frame = ttk.Frame(mode_frame)
        pwd_frame.pack(fill=tk.X, pady=4)
        ttk.Label(pwd_frame, text="用户密码:").pack(side=tk.LEFT)
        self.user_pwd = ttk.Entry(pwd_frame, show="*", width=25)
        self.user_pwd.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)

        self.owner_frame = ttk.Frame(mode_frame)
        ttk.Label(self.owner_frame, text="所有者密码:").pack(side=tk.LEFT)
        self.owner_pwd = ttk.Entry(self.owner_frame, show="*", width=25)
        self.owner_pwd.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)

        self.perm_frame = ttk.LabelFrame(mode_frame, text="权限设置（仅加密有效）", padding=5)
        self.perm_print = tk.BooleanVar(value=True)
        self.perm_copy = tk.BooleanVar(value=True)
        self.perm_modify = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.perm_frame, text="允许打印",
                        variable=self.perm_print).pack(anchor=tk.W)
        ttk.Checkbutton(self.perm_frame, text="允许复制",
                        variable=self.perm_copy).pack(anchor=tk.W)
        ttk.Checkbutton(self.perm_frame, text="允许修改",
                        variable=self.perm_modify).pack(anchor=tk.W)

        self.add_log_area(frame)
        self.add_action_button(frame, "🔐 执行操作", self.encrypt_pdf)
        self._toggle_mode()

    def _get_permissions_flag(self):
        flag = 0
        if self.perm_print.get():
            flag |= UserAccessPermissions.PRINT
        if self.perm_copy.get():
            flag |= UserAccessPermissions.EXTRACT
        if self.perm_modify.get():
            flag |= UserAccessPermissions.MODIFY
        if not flag:
            flag = UserAccessPermissions.PRINT
        return UserAccessPermissions(flag)

    def _toggle_mode(self):
        mode = self.encrypt_mode.get()
        if mode == "encrypt":
            self.owner_frame.pack(fill=tk.X, pady=2, after=self.user_pwd.master)
            self.perm_frame.pack(fill=tk.X, pady=4)
        else:
            self.owner_frame.pack_forget()
            self.perm_frame.pack_forget()

    def encrypt_pdf(self):
        self.log_running("正在处理...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return

        try:
            reader = PdfReader(src)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            mode = self.encrypt_mode.get()

            if mode == "encrypt":
                user_pwd = self.user_pwd.get().strip()
                if not user_pwd:
                    self.log_error("请输入用户密码")
                    return
                owner_pwd = self.owner_pwd.get().strip() or user_pwd
                writer.encrypt(
                    user_password=user_pwd,
                    owner_password=owner_pwd,
                    permissions_flag=self._get_permissions_flag(),
                    use_128bit=True,
                )
                out = get_unique_path(out)
                with open(out, "wb") as f:
                    writer.write(f)
                self.log_success(f"加密完成 → {os.path.basename(out)}")
            else:
                pwd = self.user_pwd.get().strip()
                if not pwd:
                    self.log_error("请输入当前密码")
                    return
                if reader.is_encrypted:
                    try:
                        reader.decrypt(pwd)
                    except Exception:
                        self.log_error("密码错误，无法解密")
                        return
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                out = get_unique_path(out)
                with open(out, "wb") as f:
                    writer.write(f)
                self.log_success(f"解密完成 → {os.path.basename(out)}")
        except Exception as e:
            self.log_error(f"操作失败: {str(e)}")


# ---------- 7. 添加水印 ----------

class WatermarkTab(BaseTab):
    """添加水印"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "💧 为PDF页面添加文字水印")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "wm_out",
                                                  default_name="加水印后.pdf")
        self.src_entry, _ = self.add_file_selector(
            frame, "源文件:", "wm",
            auto_output_entry=self.out_entry, auto_out_name="加水印后.pdf")

        opt_frame = ttk.LabelFrame(frame, text="水印设置", padding=8)
        opt_frame.pack(fill=tk.X, pady=6)

        text_frame = ttk.Frame(opt_frame)
        text_frame.pack(fill=tk.X, pady=2)
        ttk.Label(text_frame, text="水印文字:").pack(side=tk.LEFT)
        self.wm_text = ttk.Entry(text_frame)
        self.wm_text.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        self.wm_text.insert(0, "保密")

        alpha_frame = ttk.Frame(opt_frame)
        alpha_frame.pack(fill=tk.X, pady=2)
        ttk.Label(alpha_frame, text="透明度(0.1-1):").pack(side=tk.LEFT)
        self.wm_alpha = ttk.Spinbox(alpha_frame, from_=0.1, to=1.0,
                                    increment=0.1, width=8)
        self.wm_alpha.set(0.3)
        self.wm_alpha.pack(side=tk.LEFT, padx=4)

        size_frame = ttk.Frame(opt_frame)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, text="字体大小:").pack(side=tk.LEFT)
        self.wm_font_size = ttk.Spinbox(size_frame, from_=12, to=100,
                                        increment=4, width=8)
        self.wm_font_size.set(48)
        self.wm_font_size.pack(side=tk.LEFT, padx=4)

        angle_frame = ttk.Frame(opt_frame)
        angle_frame.pack(fill=tk.X, pady=2)
        ttk.Label(angle_frame, text="旋转角度:").pack(side=tk.LEFT)
        self.wm_angle = ttk.Combobox(angle_frame,
                                     values=["0", "45", "90", "135", "180", "-45"],
                                     state="readonly", width=8)
        self.wm_angle.current(1)
        self.wm_angle.pack(side=tk.LEFT, padx=4)

        color_frame = ttk.Frame(opt_frame)
        color_frame.pack(fill=tk.X, pady=2)
        ttk.Label(color_frame, text="颜色:").pack(side=tk.LEFT)
        self.wm_color = ttk.Combobox(color_frame,
                                     values=["灰色", "红色", "蓝色", "绿色", "黑色"],
                                     state="readonly", width=8)
        self.wm_color.current(0)
        self.wm_color.pack(side=tk.LEFT, padx=4)

        range_frame = ttk.Frame(opt_frame)
        range_frame.pack(fill=tk.X, pady=2)
        ttk.Label(range_frame, text="应用到页:").pack(side=tk.LEFT)
        self.wm_pages = ttk.Entry(range_frame, width=20)
        self.wm_pages.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        ttk.Label(range_frame, text="空=全部 | ODD/EVEN | 如 1,3-5",
                  foreground="#888").pack(side=tk.LEFT)

        self.add_log_area(frame)
        self.add_action_button(frame, "💧 添加水印", self.add_watermark)

    def _get_color_rgb(self):
        colors = {
            "灰色": (0.5, 0.5, 0.5),
            "红色": (0.8, 0.2, 0.2),
            "蓝色": (0.2, 0.3, 0.8),
            "绿色": (0.2, 0.6, 0.2),
            "黑色": (0.0, 0.0, 0.0),
        }
        return colors.get(self.wm_color.get(), (0.5, 0.5, 0.5))

    def add_watermark(self):
        self.log_running("正在添加水印...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()
        text = self.wm_text.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return
        if not text:
            self.log_error("请输入水印文字")
            return

        try:
            from reportlab.pdfgen import canvas as rl_canvas
            import io

            reader = PdfReader(src)
            total = len(reader.pages)
            page_filter = self.wm_pages.get().strip()
            target_pages = (parse_page_range(page_filter, total)
                            if page_filter else list(range(total)))

            alpha = safe_float(self.wm_alpha.get(), 0.3)
            font_size = safe_float(self.wm_font_size.get(), 48)
            angle = safe_float(self.wm_angle.get(), 45)
            r, g, b = self._get_color_rgb()

            writer = PdfWriter()

            for i, page in enumerate(reader.pages):
                if i in target_pages:
                    mb = page.mediabox
                    pw = float(mb.width)
                    ph = float(mb.height)

                    packet = io.BytesIO()
                    c = rl_canvas.Canvas(packet, pagesize=(pw, ph))
                    c.setFillColorRGB(r, g, b, alpha=alpha)
                    c.setFont("Helvetica", font_size)
                    c.saveState()
                    c.translate(pw / 2, ph / 2)
                    c.rotate(angle)
                    c.drawCentredString(0, 0, text)
                    c.restoreState()
                    c.save()

                    packet.seek(0)
                    watermark_pdf = PdfReader(packet)
                    watermark_page = watermark_pdf.pages[0]
                    page.merge_page(watermark_page)

                writer.add_page(page)

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)
            self.log_success(f"水印作用于 {len(target_pages)} 页 → {os.path.basename(out)}")
        except ImportError:
            self.log_error("需要安装 reportlab 库 (pip install reportlab)")
        except Exception as e:
            self.log_error(f"添加水印失败: {str(e)}")


# ---------- 8. 裁剪页面 ----------

class CropTab(BaseTab):
    """裁剪页面"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "📏 裁剪PDF页面（统一裁剪边距）")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "crop_out",
                                                  default_name="裁剪后.pdf")
        self.src_entry, _ = self.add_file_selector(
            frame, "源文件:", "crop",
            auto_output_entry=self.out_entry, auto_out_name="裁剪后.pdf")

        opt_frame = ttk.LabelFrame(frame, text="裁剪设置（单位：磅 pt）", padding=8)
        opt_frame.pack(fill=tk.X, pady=6)

        grid = ttk.Frame(opt_frame)
        grid.pack(pady=4)

        ttk.Label(grid, text="上 (Top):").grid(row=0, column=0, padx=2, pady=2, sticky=tk.E)
        self.crop_top = ttk.Entry(grid, width=8)
        self.crop_top.grid(row=0, column=1, padx=2, pady=2)
        self.crop_top.insert(0, "0")

        ttk.Label(grid, text="下 (Bottom):").grid(row=1, column=0, padx=2, pady=2, sticky=tk.E)
        self.crop_bottom = ttk.Entry(grid, width=8)
        self.crop_bottom.grid(row=1, column=1, padx=2, pady=2)
        self.crop_bottom.insert(0, "0")

        ttk.Label(grid, text="左 (Left):").grid(row=2, column=0, padx=2, pady=2, sticky=tk.E)
        self.crop_left = ttk.Entry(grid, width=8)
        self.crop_left.grid(row=2, column=1, padx=2, pady=2)
        self.crop_left.insert(0, "0")

        ttk.Label(grid, text="右 (Right):").grid(row=2, column=2, padx=2, pady=2, sticky=tk.E)
        self.crop_right = ttk.Entry(grid, width=8)
        self.crop_right.grid(row=2, column=3, padx=2, pady=2)
        self.crop_right.insert(0, "0")

        range_frame = ttk.Frame(opt_frame)
        range_frame.pack(fill=tk.X, pady=2)
        ttk.Label(range_frame, text="应用到页:").pack(side=tk.LEFT)
        self.crop_pages = ttk.Entry(range_frame, width=20)
        self.crop_pages.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        ttk.Label(range_frame, text="空=全部 | ODD/EVEN | 如 1,3-5",
                  foreground="#888").pack(side=tk.LEFT)

        preset_frame = ttk.Frame(opt_frame)
        preset_frame.pack(fill=tk.X, pady=4)
        ttk.Label(preset_frame, text="预设:").pack(side=tk.LEFT)
        ttk.Button(preset_frame, text="去除页眉页脚",
                   command=lambda: self._set_crop(50, 50, 0, 0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="去除白边",
                   command=lambda: self._set_crop(20, 20, 20, 20)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="大幅裁剪",
                   command=lambda: self._set_crop(80, 80, 40, 40)).pack(side=tk.LEFT, padx=2)
        self.add_odd_even_buttons(opt_frame, self.crop_pages)

        self.add_log_area(frame)
        self.add_action_button(frame, "📏 开始裁剪", self.crop_pdf)

    def _set_crop(self, top, bottom, left, right):
        self.crop_top.delete(0, tk.END)
        self.crop_top.insert(0, str(top))
        self.crop_bottom.delete(0, tk.END)
        self.crop_bottom.insert(0, str(bottom))
        self.crop_left.delete(0, tk.END)
        self.crop_left.insert(0, str(left))
        self.crop_right.delete(0, tk.END)
        self.crop_right.insert(0, str(right))

    def crop_pdf(self):
        self.log_running("正在裁剪...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return

        try:
            reader = PdfReader(src)
            writer = PdfWriter()
            total = len(reader.pages)

            top = safe_int(self.crop_top.get(), 0)
            bottom = safe_int(self.crop_bottom.get(), 0)
            left = safe_int(self.crop_left.get(), 0)
            right = safe_int(self.crop_right.get(), 0)

            if top == 0 and bottom == 0 and left == 0 and right == 0:
                self.log_error("请设置裁剪值")
                return

            page_filter = self.crop_pages.get().strip()
            target_pages = (parse_page_range(page_filter, total)
                            if page_filter else list(range(total)))

            for i, page in enumerate(reader.pages):
                if i in target_pages:
                    mb = page.mediabox
                    pw = float(mb.width)
                    ph = float(mb.height)

                    new_left = left
                    new_bottom = bottom
                    new_right = pw - right
                    new_top = ph - top

                    if new_right > new_left and new_top > new_bottom:
                        page.cropbox.lower_left = (new_left, new_bottom)
                        page.cropbox.upper_right = (new_right, new_top)
                        page.mediabox = page.cropbox

                writer.add_page(page)

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)
            self.log_success(f"裁剪完成 → {os.path.basename(out)}")
        except Exception as e:
            self.log_error(f"裁剪失败: {str(e)}")


# ---------- 9. 页面排序 ----------

class ReorderTab(BaseTab):
    """页面排序"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "🔀 重新排列PDF页面顺序")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "reorder_out",
                                                  default_name="重排后.pdf")
        self.src_entry, self.src_info = self.add_file_selector(
            frame, "源文件:", "reorder",
            auto_output_entry=self.out_entry, auto_out_name="重排后.pdf")

        opt_frame = ttk.LabelFrame(frame, text="排序设置", padding=8)
        opt_frame.pack(fill=tk.X, pady=6)

        ttk.Label(opt_frame, text="新顺序(逗号分隔,如: 3,1,5-7,2)").pack(anchor=tk.W)
        ttk.Label(opt_frame, text="支持: 单页: 3,  范围: 5-7,  ODD/EVEN",
                  foreground="#888").pack(anchor=tk.W)
        self.order_entry = ttk.Entry(opt_frame)
        self.order_entry.pack(fill=tk.X, padx=0, pady=4)

        quick_frame = ttk.Frame(opt_frame)
        quick_frame.pack(fill=tk.X, pady=4)
        ttk.Label(quick_frame, text="快捷:").pack(side=tk.LEFT)
        ttk.Button(quick_frame, text="倒序",
                   command=lambda: self._set_entry(self.order_entry, "REVERSE")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="偶数页在前",
                   command=lambda: self._set_entry(self.order_entry, "EVEN_FIRST")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="奇数页在前",
                   command=lambda: self._set_entry(self.order_entry, "ODD_FIRST")).pack(side=tk.LEFT, padx=2)

        self.add_log_area(frame)
        self.add_action_button(frame, "🔀 重排页面", self.reorder_pdf)

    def reorder_pdf(self):
        self.log_running("正在重排...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()
        order_str = self.order_entry.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return
        if not order_str:
            self.log_error("请输入新的页面顺序")
            return

        try:
            reader = PdfReader(src)
            total = len(reader.pages)

            cmd = order_str.upper()
            if cmd == "REVERSE":
                new_order = list(range(total - 1, -1, -1))
            elif cmd == "EVEN_FIRST":
                evens = [i for i in range(total) if (i + 1) % 2 == 0]
                odds = [i for i in range(total) if (i + 1) % 2 == 1]
                new_order = evens + odds
            elif cmd == "ODD_FIRST":
                odds = [i for i in range(total) if (i + 1) % 2 == 1]
                evens = [i for i in range(total) if (i + 1) % 2 == 0]
                new_order = odds + evens
            else:
                new_order = parse_page_range_ordered(order_str, total)

            if not new_order:
                self.log_error("未找到有效的页码")
                return
            if len(new_order) > total:
                self.log_error(f"指定的页数 ({len(new_order)}) 超过总页数 ({total})")
                return

            writer = PdfWriter()
            for p in new_order:
                writer.add_page(reader.pages[p])

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)
            self.log_success(f"重排 {len(new_order)} 页 → {os.path.basename(out)}")
        except Exception as e:
            self.log_error(f"重排失败: {str(e)}")


# ---------- 10. 编辑元数据 ----------

class MetadataTab(BaseTab):
    """编辑元数据"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "🏷️ 查看和编辑PDF元数据信息")
        self.add_separator(frame)

        self.src_entry, _ = self.add_file_selector(frame, "源文件:", "meta")

        meta_frame = ttk.LabelFrame(frame, text="元数据信息", padding=8)
        meta_frame.pack(fill=tk.X, pady=6)

        fields = [
            ("标题:", "meta_title"),
            ("作者:", "meta_author"),
            ("主题:", "meta_subject"),
            ("关键词:", "meta_keywords"),
            ("制作者:", "meta_producer"),
        ]
        self.meta_entries = {}
        for label, attr in fields:
            rf = ttk.Frame(meta_frame)
            rf.pack(fill=tk.X, pady=1)
            ttk.Label(rf, text=label, width=8).pack(side=tk.LEFT)
            entry = ttk.Entry(rf)
            entry.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
            self.meta_entries[attr] = entry

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="📖 读取元数据",
                   command=self.load_metadata).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="💾 保存到新文件",
                   command=self.save_metadata).pack(side=tk.LEFT, padx=4)

        self.meta_info = ttk.Label(frame, text="", foreground="#636e72")
        self.meta_info.pack(anchor=tk.W, pady=2)
        self.add_log_area(frame)

    def load_metadata(self):
        src = self.src_entry.get().strip()
        if not src:
            self.log_error("请先选择PDF文件")
            return
        try:
            reader = PdfReader(src)
            meta = reader.metadata
            if meta:
                self.meta_entries["meta_title"].delete(0, tk.END)
                self.meta_entries["meta_title"].insert(0, meta.title or "")
                self.meta_entries["meta_author"].delete(0, tk.END)
                self.meta_entries["meta_author"].insert(0, meta.author or "")
                self.meta_entries["meta_subject"].delete(0, tk.END)
                self.meta_entries["meta_subject"].insert(0, meta.subject or "")
                self.meta_entries["meta_keywords"].delete(0, tk.END)
                self.meta_entries["meta_keywords"].insert(0, meta.keywords or "")
                self.meta_entries["meta_producer"].delete(0, tk.END)
                self.meta_entries["meta_producer"].insert(0, meta.producer or "")
                self.log_success("元数据已加载")
            else:
                self.log_error("该PDF无元数据信息")
        except Exception as e:
            self.log_error(f"读取失败: {str(e)}")

    def save_metadata(self):
        self.log_running("正在保存...")
        src = self.src_entry.get().strip()
        if not src:
            self.log_error("请先选择PDF文件")
            return

        src_dir = os.path.dirname(src) if src else ""
        out = filedialog.asksaveasfilename(
            title="保存修改后的PDF",
            initialdir=src_dir if src_dir else None,
            initialfile="元数据修改后.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if not out:
            self.log_error("请选择保存位置")
            return

        try:
            reader = PdfReader(src)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            meta_data = {
                "/Title": self.meta_entries["meta_title"].get().strip(),
                "/Author": self.meta_entries["meta_author"].get().strip(),
                "/Subject": self.meta_entries["meta_subject"].get().strip(),
                "/Keywords": self.meta_entries["meta_keywords"].get().strip(),
                "/Producer": self.meta_entries["meta_producer"].get().strip(),
            }
            meta_data = {k: v for k, v in meta_data.items() if v}
            if meta_data:
                writer.add_metadata(meta_data)

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)
            self.log_success(f"元数据已保存 → {os.path.basename(out)}")
        except Exception as e:
            self.log_error(f"保存失败: {str(e)}")


# ---------- 11. 合并PDF ----------

class MergeTab(BaseTab):
    """合并PDF"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "🔗 将多个PDF文件按顺序合并为一个PDF")
        self.add_separator(frame)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="➕ 添加文件",
                   command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="⬆️ 上移",
                   command=lambda: self.move_item(-1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="⬇️ 下移",
                   command=lambda: self.move_item(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ 移除选中",
                   command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 清空",
                   command=self.clear_files).pack(side=tk.LEFT, padx=2)

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=3)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.file_listbox = tk.Listbox(list_frame,
                                       yscrollcommand=scrollbar.set,
                                       font=("微软雅黑", 9))
        scrollbar.config(command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.out_entry = self.add_output_selector(frame, "输出:", "merge_out",
                                                  default_name="合并结果.pdf")
        self._first_file_set_out = False

        self.add_log_area(frame)
        self.add_action_button(frame, "🚀 开始合并", self.merge_pdfs)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if not files:
            return
        flist = self.app.files
        for f in files:
            if f not in flist:
                flist.append(f)
                self.file_listbox.insert(tk.END, f"  {os.path.basename(f)}  ({get_file_info(f)})")
                if not self._first_file_set_out:
                    src_dir = os.path.dirname(f)
                    self.out_entry.delete(0, tk.END)
                    self.out_entry.insert(0, os.path.join(src_dir, "合并结果.pdf"))
                    self._first_file_set_out = True

    def move_item(self, direction):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        flist = self.app.files
        if new_idx < 0 or new_idx >= len(flist):
            return
        flist[idx], flist[new_idx] = flist[new_idx], flist[idx]
        self._refresh_listbox()
        self.file_listbox.selection_set(new_idx)

    def remove_selected(self):
        sel = self.file_listbox.curselection()
        if sel:
            idx = sel[0]
            del self.app.files[idx]
            self._refresh_listbox()
            if not self.app.files:
                self._first_file_set_out = False

    def clear_files(self):
        self.app.files.clear()
        self._refresh_listbox()
        self._first_file_set_out = False

    def _refresh_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for f in self.app.files:
            self.file_listbox.insert(tk.END, f"  {os.path.basename(f)}  ({get_file_info(f)})")

    def merge_pdfs(self):
        self.log_running("正在合并...")
        flist = self.app.files
        if not flist:
            self.log_error("请先添加要合并的PDF文件")
            return
        output = self.out_entry.get().strip()
        if not output:
            self.log_error("请设置输出文件名")
            return

        try:
            writer = PdfWriter()
            total_pages = 0
            for f in flist:
                reader = PdfReader(f)
                for page in reader.pages:
                    writer.add_page(page)
                total_pages += len(reader.pages)
            output = get_unique_path(output)
            with open(output, "wb") as out:
                writer.write(out)
            self.log_success(f"合并 {len(flist)} 个文件, {total_pages} 页")
        except Exception as e:
            self.log_error(f"合并失败: {str(e)}")


# ---------- 12. 页面缩放 ----------

class ScaleTab(BaseTab):
    """页面缩放"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "🖼️ 按比例缩放PDF页面内容")
        self.add_separator(frame)

        self.out_entry = self.add_output_selector(frame, "输出:", "scale_out",
                                                  default_name="缩放后.pdf")
        self.src_entry, self.src_info = self.add_file_selector(
            frame, "源文件:", "scale",
            auto_output_entry=self.out_entry, auto_out_name="缩放后.pdf")

        opt_frame = ttk.LabelFrame(frame, text="缩放设置", padding=8)
        opt_frame.pack(fill=tk.X, pady=6)

        scale_frame = ttk.Frame(opt_frame)
        scale_frame.pack(fill=tk.X, pady=4)
        ttk.Label(scale_frame, text="缩放比例(%):").pack(side=tk.LEFT)
        self.scale_spin = ttk.Spinbox(scale_frame, from_=10, to=500,
                                      increment=5, width=8)
        self.scale_spin.set(100)
        self.scale_spin.pack(side=tk.LEFT, padx=4)
        ttk.Label(scale_frame, text="(10~500%)", foreground="#888").pack(side=tk.LEFT)

        # 缩放比例预设
        scale_preset = ttk.Frame(opt_frame)
        scale_preset.pack(fill=tk.X, pady=2)
        ttk.Label(scale_preset, text="比例:").pack(side=tk.LEFT)
        for pct, label in [(50, "50%"), (70, "70%"), (100, "100%"), (120, "120%"), (150, "150%"), (200, "200%")]:
            ttk.Button(scale_preset, text=label,
                       command=lambda v=pct: self._set_scale(v)).pack(side=tk.LEFT, padx=2)

        # 打印尺寸预设
        print_preset = ttk.Frame(opt_frame)
        print_preset.pack(fill=tk.X, pady=2)
        ttk.Label(print_preset, text="尺寸:").pack(side=tk.LEFT)
        self.PAPER_SIZES = {
            "A4":      (595.28, 841.89),
            "A3":      (841.89, 1190.55),
            "A5":      (420.94, 595.28),
            "Letter":  (612.0,  792.0),
            "Legal":   (612.0,  1008.0),
            "Tabloid": (792.0,  1224.0),
        }
        for name in ["A4", "A3", "Letter", "Legal"]:
            ttk.Button(print_preset, text=name,
                       command=lambda n=name: self._set_paper_size(n)).pack(side=tk.LEFT, padx=2)

        range_frame = ttk.Frame(opt_frame)
        range_frame.pack(fill=tk.X, pady=2)
        ttk.Label(range_frame, text="应用到页:").pack(side=tk.LEFT)
        self.scale_pages = ttk.Entry(range_frame, width=20)
        self.scale_pages.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        ttk.Label(range_frame, text="空=全部 | ODD/EVEN | 如 1,3-5",
                  foreground="#888").pack(side=tk.LEFT)
        self.add_odd_even_buttons(opt_frame, self.scale_pages)

        self.add_log_area(frame)
        self.add_action_button(frame, "🖼️ 开始缩放", self.scale_pdf)

    def _set_scale(self, val):
        self.scale_spin.delete(0, tk.END)
        self.scale_spin.insert(0, str(val))

    def _set_paper_size(self, name):
        """按标准纸张尺寸设置缩放比例"""
        src = self.src_entry.get().strip()
        if not src:
            self.log_error("请先选择PDF文件")
            return
        try:
            reader = PdfReader(src)
            # 获取第一页的尺寸，计算缩放比
            mb = reader.pages[0].mediabox
            pw = float(mb.width)
            ph = float(mb.height)
            target_w, target_h = self.PAPER_SIZES[name]
            # 保持比例缩放，取较小的缩放比
            ratio_w = target_w / pw
            ratio_h = target_h / ph
            ratio = min(ratio_w, ratio_h) * 100
            ratio = round(ratio, 1)
            self._set_scale(ratio)
            self.log_success(f"设为{name}比例: {ratio}%")
        except Exception as e:
            self.log_error(f"计算尺寸失败: {str(e)}")

    def scale_pdf(self):
        self.log_running("正在缩放...")
        src = self.src_entry.get().strip()
        out = self.out_entry.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out:
            self.log_error("请设置输出文件名")
            return

        try:
            ratio = safe_float(self.scale_spin.get(), 100) / 100.0
            if ratio < 0.1 or ratio > 5.0:
                self.log_error("缩放比例范围为 10%~500%")
                return

            reader = PdfReader(src)
            total = len(reader.pages)
            page_filter = self.scale_pages.get().strip()
            target_pages = (parse_page_range(page_filter, total)
                            if page_filter else list(range(total)))

            writer = PdfWriter()

            for i, page in enumerate(reader.pages):
                if i in target_pages:
                    mb = page.mediabox
                    pw = float(mb.width)
                    ph = float(mb.height)
                    new_w = pw * ratio
                    new_h = ph * ratio
                    page.scale(ratio, ratio)
                    page.mediabox.lower_left = (0, 0)
                    page.mediabox.upper_right = (new_w, new_h)
                writer.add_page(page)

            out = get_unique_path(out)
            with open(out, "wb") as f:
                writer.write(f)
            self.log_success(f"缩放 {ratio*100:.0f}%，作用于 {len(target_pages)} 页")
        except Exception as e:
            self.log_error(f"缩放失败: {str(e)}")


# ---------- 13. 页面信息统计 ----------

class InfoTab(BaseTab):
    """PDF信息统计"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "📊 查看PDF文件详细信息")
        self.add_separator(frame)

        self.src_entry, _ = self.add_file_selector(frame, "文件:", "info")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="📊 分析PDF",
                   command=self.analyze_pdf).pack(side=tk.LEFT, padx=4)

        self.info_text = tk.Text(frame, height=16, font=("Consolas", 9),
                                 wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=4)

        scrollbar = ttk.Scrollbar(self.info_text, orient=tk.VERTICAL,
                                  command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)

    def analyze_pdf(self):
        src = self.src_entry.get().strip()
        if not src:
            return messagebox.showwarning("提示", "请先选择PDF文件")

        try:
            reader = PdfReader(src)
            total = len(reader.pages)
            meta = reader.metadata
            fsize = os.path.getsize(src)

            lines = []
            lines.append(f"{'='*50}")
            lines.append(f"  文件信息")
            lines.append(f"{'='*50}")
            lines.append(f"  文件名:     {os.path.basename(src)}")
            lines.append(f"  文件路径:   {src}")
            lines.append(f"  文件大小:   {self._fmt_size(fsize)}")
            lines.append(f"  PDF版本:    {reader.pdf_header}")
            lines.append(f"  总页数:     {total} 页")
            lines.append(f"  奇数页数:   {(total + 1) // 2} 页")
            lines.append(f"  偶数页数:   {total // 2} 页")
            lines.append(f"  加密状态:   {'是 🔒' if reader.is_encrypted else '否 🔓'}")
            lines.append("")

            if meta is not None:
                lines.append(f"{'='*50}")
                lines.append(f"  元数据")
                lines.append(f"{'='*50}")
                lines.append(f"  标题:      {getattr(meta, 'title', '') or '(空)'}")
                lines.append(f"  作者:      {getattr(meta, 'author', '') or '(空)'}")
                lines.append(f"  主题:      {getattr(meta, 'subject', '') or '(空)'}")
                lines.append(f"  关键词:    {getattr(meta, 'keywords', '') or '(空)'}")
                lines.append(f"  制作者:    {getattr(meta, 'producer', '') or '(空)'}")
                lines.append("")

            lines.append(f"{'='*50}")
            lines.append(f"  页面详情（前50页）")
            lines.append(f"{'='*50}")
            for i in range(min(total, 50)):
                page = reader.pages[i]
                mb = page.mediabox
                pw = float(mb.width)
                ph = float(mb.height)
                rot = page.get("/Rotate", 0)
                oe = "奇" if (i + 1) % 2 == 1 else "偶"
                lines.append(f"  第 {i+1:3d} 页 [{oe}] | 尺寸: {pw:.0f}x{ph:.0f} pt | 旋转: {rot}°")
            if total > 50:
                lines.append(f"  ... 还有 {total - 50} 页未显示")

            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, "\n".join(lines))
            self.info_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("❌ 错误", f"分析失败: {str(e)}")

    def _fmt_size(self, size_bytes):
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"


# ============================================================
#  格式转换标签页
# ============================================================

# ---------- 14. PDF⇄图片 ----------

class PdfToImageTab(BaseTab):
    """PDF⇄图片 互相转换"""

    def _build(self):
        frame = self.frame
        self.add_title(frame, "🖼️ PDF⇄图片")
        self.add_separator(frame)

        # 模式选择
        mode_frame = ttk.Frame(frame)
        mode_frame.pack(fill=tk.X, pady=3)
        ttk.Label(mode_frame, text="转换模式:").pack(side=tk.LEFT)
        self.convert_mode = ttk.Combobox(mode_frame,
                                         values=["PDF → 图片", "图片 → PDF"],
                                         state="readonly", width=16)
        self.convert_mode.current(0)
        self.convert_mode.pack(side=tk.LEFT, padx=4)
        self.convert_mode.bind("<<ComboboxSelected>>", self._on_mode_change)

        # 文件选择区域
        self.src_entry, self.src_info = self.add_file_selector(
            frame, "源文件:", "pi")

        # 输出目录（PDF→图片模式）
        self.out_dir_entry = self.add_output_dir_selector(frame, "输出到:", "pi_dir")

        # 分辨率设置
        dpi_frame = ttk.Frame(frame)
        dpi_frame.pack(fill=tk.X, pady=3)
        ttk.Label(dpi_frame, text="分辨率 (DPI):").pack(side=tk.LEFT)
        self.dpi_spin = ttk.Spinbox(dpi_frame, from_=72, to=600, increment=72, width=6)
        self.dpi_spin.set(300)
        self.dpi_spin.pack(side=tk.LEFT, padx=4)
        ttk.Label(dpi_frame, text="(72=原始尺寸, 300=印刷质量)").pack(side=tk.LEFT)

        # 输出文件（图片→PDF模式，默认隐藏）
        self.out_entry = self.add_output_selector(frame, "输出:", "pi_out",
                                                  default_name="合并图片.pdf")
        self.out_entry.pack_forget()  # 默认隐藏

        # 图片列表（图片→PDF模式）
        self.img_list_frame = ttk.LabelFrame(frame, text="图片列表（选择图片文件）", padding=5)
        btn_row = ttk.Frame(self.img_list_frame)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="➕ 添加图片",
                   command=self.add_images).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="⬆️ 上移",
                   command=lambda: self._move_img(-1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="⬇️ 下移",
                   command=lambda: self._move_img(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="🗑️ 移除",
                   command=self.remove_img).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="🔄 清空",
                   command=self.clear_imgs).pack(side=tk.LEFT, padx=2)

        list_scroll = ttk.Scrollbar(self.img_list_frame, orient=tk.VERTICAL)
        self.img_listbox = tk.Listbox(self.img_list_frame,
                                      yscrollcommand=list_scroll.set,
                                      font=("微软雅黑", 9))
        list_scroll.config(command=self.img_listbox.yview)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.img_listbox.pack(fill=tk.BOTH, expand=True)

        self._image_files = []

        self.add_log_area(frame)
        self.add_action_button(frame, "🔄 开始转换", self.convert)

    def _custom_browse(self, entry, key, auto_output_entry=None, auto_out_name=None):
        """PDF→图片模式：选择PDF，输出目录自动设为源文件目录"""
        d = self.convert_mode.get()
        if "PDF → 图片" in d:
            path = filedialog.askopenfilename(
                title="选择PDF文件",
                filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
            )
        else:
            # 图片→PDF不需要单独选源文件，用图片列表
            self.add_images()
            return
        if not path:
            return
        entry.delete(0, tk.END)
        entry.insert(0, path)
        info_label = getattr(self, f"{key}_info", None)
        if info_label:
            if path.lower().endswith('.pdf'):
                info_label.config(text=get_file_info(path))
            else:
                info_label.config(text=f"📄 {os.path.basename(path)}")
        # ★ 自动设置输出目录为源文件所在目录
        src_dir = os.path.dirname(path)
        self.out_dir_entry.delete(0, tk.END)
        self.out_dir_entry.insert(0, src_dir)

    def _on_mode_change(self, event=None):
        d = self.convert_mode.get()
        src_frame = self.pi_frame  # 源文件行的框架 #type:ignore
        if "PDF → 图片" in d:
            # 显示源文件和输出目录
            src_frame.pack(fill=tk.X, pady=3)
            self.out_dir_entry.pack()
            self.out_entry.pack_forget()
            self.img_list_frame.pack_forget()
        else:
            # 图片→PDF：隐藏源文件，显示输出文件和图片列表
            src_frame.pack_forget()
            self.out_dir_entry.pack_forget()
            self.out_entry.pack()
            self.img_list_frame.pack(fill=tk.BOTH, expand=True, pady=4)
            # 自动设置输出文件名
            if self._image_files:
                src_dir = os.path.dirname(self._image_files[0])
                self.out_entry.delete(0, tk.END)
                self.out_entry.insert(0, os.path.join(src_dir, "合并图片.pdf"))

    def add_images(self):
        files = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp"),
                       ("所有文件", "*.*")]
        )
        if not files:
            return
        was_empty = len(self._image_files) == 0
        for f in files:
            if f not in self._image_files:
                self._image_files.append(f)
                self.img_listbox.insert(tk.END, f"  {os.path.basename(f)}")
        if was_empty and self._image_files:
            src_dir = os.path.dirname(self._image_files[0])
            self.out_entry.delete(0, tk.END)
            self.out_entry.insert(0, os.path.join(src_dir, "合并图片.pdf"))

    def _move_img(self, direction):
        sel = self.img_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self._image_files):
            return
        self._image_files[idx], self._image_files[new_idx] = \
            self._image_files[new_idx], self._image_files[idx]
        self._refresh_img_list()
        self.img_listbox.selection_set(new_idx)

    def remove_img(self):
        sel = self.img_listbox.curselection()
        if sel:
            idx = sel[0]
            del self._image_files[idx]
            self._refresh_img_list()

    def clear_imgs(self):
        self._image_files.clear()
        self._refresh_img_list()

    def _refresh_img_list(self):
        self.img_listbox.delete(0, tk.END)
        for f in self._image_files:
            self.img_listbox.insert(tk.END, f"  {os.path.basename(f)}")

    def convert(self):
        self.log_running("正在转换...")
        d = self.convert_mode.get()
        try:
            if "PDF → 图片" in d:
                self._pdf_to_images()
            else:
                self._images_to_pdf()
        except ImportError as e:
            self.log_error(f"缺少依赖: {str(e)}")
        except Exception as e:
            self.log_error(f"转换失败: {str(e)}")

    def _pdf_to_images(self):
        """PDF→图片：每页转为PNG，保持原页面尺寸和分辨率（72 DPI = 1pt = 1px）"""
        try:
            import fitz
        except ImportError:
            raise ImportError("pymupdf")

        src = self.src_entry.get().strip()
        out_dir = self.out_dir_entry.get().strip()

        if not src:
            self.log_error("请选择PDF文件")
            return
        if not out_dir:
            self.log_error("请选择输出目录")
            return
        os.makedirs(out_dir, exist_ok=True)

        pdf = fitz.open(src)
        base_name = os.path.splitext(os.path.basename(src))[0]
        # 使用用户设置的DPI
        dpi = safe_int(self.dpi_spin.get(), 300)
        zoom = dpi / 72  # 1pt at DPI dpi
        mat = fitz.Matrix(zoom, zoom)

        for i in range(len(pdf)):
            page = pdf[i]
            pix = page.get_pixmap(matrix=mat)
            filename = f"{base_name}_p{i+1:03d}.png"
            out_path = get_unique_path(os.path.join(out_dir, filename))
            pix.save(out_path)

        pdf.close()
        self.log_success(f"PDF转图片完成，保存至 {out_dir}")

    def _images_to_pdf(self):
        """图片→PDF：合并图片为PDF，保持每张图的原始尺寸和分辨率"""
        import img2pdf
        from PIL import Image

        if not self._image_files:
            self.log_error("请先添加要合并的图片")
            return
        out = self.out_entry.get().strip()
        if not out:
            self.log_error("请设置输出文件名")
            return

        # 按图片原有DPI布局，img2pdf自动保持每张图的原始尺寸
        out = get_unique_path(out)
        pdf_bytes = img2pdf.convert(self._image_files)
        if pdf_bytes is None:
            raise ValueError("img2pdf 转换失败，返回空结果")
        with open(out, "wb") as f:
            f.write(pdf_bytes)

        self.log_success(f"合并 {len(self._image_files)} 张图片 → {os.path.basename(out)}")


# ============================================================
#  主应用
# ============================================================

class PDFToolPro:
    """专业PDF编辑工具主应用"""

    def __init__(self, root):
        self.root = root
        self.root.title("专业PDF编辑工具")
        self.root.geometry("1400x820")
        self.root.minsize(1100, 680)
        self.root.resizable(True, True)

        self.files: list = []

        self.tab_classes = [
            ("🔗  合并PDF",     MergeTab),
            ("✂️  拆分PDF",     SplitTab),
            ("🔄  旋转页面",    RotateTab),
            ("📋  提取页面",    ExtractTab),
            ("🗑️  删除页面",    DeletePagesTab),
            ("📄  插入空白页",  InsertBlankTab),
            ("🔐  加密/解密",   EncryptTab),
            ("💧  添加水印",    WatermarkTab),
            ("📏  裁剪页面",    CropTab),
            ("🖼️  页面缩放",    ScaleTab),
            ("🔀  页面排序",    ReorderTab),
            ("🏷️  编辑元数据",  MetadataTab),
            ("📊  信息统计",    InfoTab),
            ("🖼️  PDF⇄图片", PdfToImageTab),
        ]

        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self.root,
                           text="📝 专业PDF编辑工具 | 输出默认到源文件目录 | 同名文件自动加后缀不覆盖 | 支持 PDF⇄图片",
                           font=("微软雅黑", 9), foreground="#555")
        header.pack(fill=tk.X, padx=10, pady=(6, 0))

        main_frame = ttk.Frame(self.root, padding=8)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}
        for name, cls in self.tab_classes:
            tab_instance = cls(self.notebook, self)
            self.notebook.add(tab_instance.frame, text=name)
            self.tabs[name] = tab_instance

    def get_tab(self, name_or_index):
        if isinstance(name_or_index, int):
            name = self.tab_classes[name_or_index][0]
            return self.tabs.get(name)
        return self.tabs.get(name_or_index)


def main():
    root = tk.Tk()

    style = ttk.Style()
    available = style.theme_names()
    for theme in ("vista", "clam", "alt", "default"):
        if theme in available:
            style.theme_use(theme)
            break

    style.configure("Accent.TButton", font=("微软雅黑", 10, "bold"))
    style.configure("TLabel", font=("微软雅黑", 9))
    style.configure("TLabelframe.Label", font=("微软雅黑", 9, "bold"))

    app = PDFToolPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()