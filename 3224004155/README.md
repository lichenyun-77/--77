# 第一次个人编程作业：论文查重

## 运行环境

- Python 3.10 或更高版本
- 程序本身只使用标准库，无运行时第三方依赖。

## 使用方法

```powershell
python main.py <原文绝对路径> <抄袭版绝对路径> <答案文件绝对路径>
```

例如：

```powershell
python main.py C:\tests\orig.txt C:\tests\orig_add.txt C:\tests\ans.txt
```

答案文件仅包含相似度，格式为 `0.00` 到 `1.00`，保留两位小数。

## 算法

程序先进行 Unicode 规范化、英文大小写统一，并忽略空白字符；随后以字符为单位调用 Python 标准库 `difflib.SequenceMatcher` 获取匹配字符块的相似度。该方法可自然处理文本的增、删、改操作。

## 测试

安装 pytest 后运行：

```powershell
python -m pytest -q
```

测试覆盖完全相同、完全不同、空文本、空白符、大小写、全角字符、增加、删除、替换、文件缺失和命令行写出等场景。
