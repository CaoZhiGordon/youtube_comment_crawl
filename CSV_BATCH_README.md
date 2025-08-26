# 🎬 YouTube评论批量下载工具 (CSV版本)

一个强大的Python工具，可以批量搜索YouTube视频并下载评论，**默认输出CSV格式**，方便数据分析。

## ✨ 主要功能

### 🔍 智能搜索
- **关键词批量搜索**: 支持多个关键词同时搜索
- **视频类型识别**: 自动识别普通视频和Shorts
- **搜索结果导出**: JSON、CSV、TXT多格式保存

### ⬇️ 批量下载
- **CSV格式输出**: 默认导出为CSV文件，便于Excel/数据分析
- **JSON格式支持**: 可选择JSON格式输出
- **智能转换**: 自动将原始JSON数据转换为结构化CSV
- **批量处理**: 支持大量视频的批量评论下载

### 📊 CSV数据结构

导出的CSV文件包含以下字段：

| 字段名 | 说明 | 示例 |
|--------|------|------|
| 视频ID | YouTube视频唯一标识 | `dQw4w9WgXcQ` |
| 视频标题 | 视频的完整标题 | `Rick Astley - Never Gonna Give You Up` |
| 视频URL | 视频的完整链接 | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` |
| 评论ID | 评论的唯一标识 | `UgxKREWxIgDrw8w2bTp4AaABAg` |
| 评论内容 | 评论的文本内容 | `Great song!` |
| 作者 | 评论作者的用户名 | `@user123` |
| 作者频道ID | 评论作者的频道ID | `UCxxxxxxxxxxxxxxxx` |
| 点赞数 | 评论获得的点赞数 | `42` |
| 回复数 | 评论的回复数量 | `5` |
| 发布时间 | 评论发布的时间文本 | `2 days ago` |
| 发布时间戳 | 评论发布的具体时间 | `2024-01-15T10:30:00` |
| 是否置顶 | 是否为置顶评论 | `True/False` |
| 是否作者回复 | 是否为视频作者回复 | `True/False` |
| 照片URL | 评论作者头像链接 | `https://...` |
| 是否有心形标记 | 是否被视频作者点心 | `True/False` |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行工具

```bash
python3 batch_comment_downloader.py
```

### 3. 选择模式

工具提供4种操作模式：

1. **完整流程** - 搜索视频URL + 下载评论（推荐）
2. **仅搜索URL** - 只搜索并保存视频链接
3. **从文件下载** - 从已有URL文件批量下载评论
4. **退出程序**

## 📋 使用示例

### 完整流程示例

1. 选择模式 `1` (完整流程)
2. 输入关键词: `蔡依林,周杰伦,邓紫棋`
3. 设置参数:
   - 每个关键词最大视频数: `20`
   - 页面滚动次数: `5`
   - 每个视频评论数量限制: `100`
   - 排序方式: `1` (最新)
   - 语言设置: `zh` (中文)
   - **输出格式: `csv`** (CSV格式)
   - 下载间隔: `2` 秒

### 输出结果

```
📂 batch_comments_output/
├── 📂 urls/                    # URL搜索结果
│   ├── video_urls_20240115_143022.json
│   ├── video_urls_20240115_143022.csv
│   └── urls_only_20240115_143022.txt
├── 📂 comments/                # 评论CSV文件
│   ├── dQw4w9WgXcQ_Rick Astley Never Gonna Give You Up.csv
│   ├── 9bZkp7q19f0_PSY GANGNAM STYLE.csv
│   └── ...
└── 📂 logs/                    # 下载日志
    └── download_log_20240115_143022.txt
```

## 🧪 测试功能

运行测试脚本验证CSV功能：

```bash
python3 test_csv_batch.py
```

## ⚙️ 高级配置

### 输出格式选择

- **CSV格式** (推荐): 便于Excel打开和数据分析
- **JSON格式**: 保留完整的原始数据结构

### 排序方式

- `0` = 按热门排序 (点赞数高的评论优先)
- `1` = 按最新排序 (时间新的评论优先)

### 语言设置

- `zh` = 中文评论优先
- `en` = 英文评论优先
- 留空 = 自动检测

## 📊 数据分析建议

CSV文件可以直接导入到：

- **Excel**: 双击打开，支持筛选和透视表
- **Python Pandas**: `pd.read_csv('文件名.csv')`
- **R**: `read.csv('文件名.csv')`
- **Power BI**: 直接导入CSV数据源
- **Tableau**: 连接到CSV文件

### Python分析示例

```python
import pandas as pd

# 读取CSV文件
df = pd.read_csv('dQw4w9WgXcQ_Rick Astley Never Gonna Give You Up.csv')

# 基本统计
print(f"总评论数: {len(df)}")
print(f"平均点赞数: {df['点赞数'].mean():.1f}")
print(f"最热评论: {df.loc[df['点赞数'].idxmax(), '评论内容']}")

# 评论长度分析
df['评论长度'] = df['评论内容'].str.len()
print(f"平均评论长度: {df['评论长度'].mean():.1f} 字符")

# 作者活跃度
author_counts = df['作者'].value_counts()
print(f"最活跃评论者: {author_counts.index[0]} ({author_counts.iloc[0]} 条评论)")
```

## 🛠️ 常见问题

### Q: CSV文件乱码怎么办？
A: CSV文件使用UTF-8-BOM编码，Excel应该能正确显示中文。如果仍有问题，可以：
1. 用记事本打开CSV文件
2. 另存为时选择"UTF-8"编码
3. 重新用Excel打开

### Q: 如何批量分析多个CSV文件？
A: 使用Python脚本：

```python
import pandas as pd
import glob

# 读取所有CSV文件
csv_files = glob.glob('batch_comments_output/comments/*.csv')
all_data = []

for file in csv_files:
    df = pd.read_csv(file)
    all_data.append(df)

# 合并所有数据
combined_df = pd.concat(all_data, ignore_index=True)
print(f"总评论数: {len(combined_df)}")
```

### Q: 下载速度慢怎么办？
A: 可以调整参数：
- 减少评论数量限制 (如改为50)
- 增加下载间隔避免被限制
- 使用多线程版本 (高级用户)

## 🔧 技术特点

- **自动格式转换**: JSON → CSV 无缝转换
- **中文友好**: 完美支持中文评论和用户名
- **错误处理**: 单个视频失败不影响整体流程
- **进度显示**: 实时显示下载进度和统计
- **日志记录**: 详细的操作日志便于问题排查

## 📈 适用场景

- **学术研究**: 社交媒体情感分析
- **市场调研**: 用户反馈收集
- **内容分析**: 视频评论趋势分析
- **竞品分析**: 竞争对手内容反馈
- **数据挖掘**: 大规模文本数据收集

---

🎯 **开始使用**: `python3 batch_comment_downloader.py`

📊 **CSV优势**: 直接用Excel打开，无需额外处理！ 