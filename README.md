# YouTube评论批量下载工具 🎬

![GitHub](https://img.shields.io/github/license/CaoZhiGordon/youtube_comment_crawl)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-lightgrey.svg)

一个基于 `youtube-comment-downloader` 包的**批量YouTube评论下载工具**，支持关键词搜索、批量URL爬取和批量评论下载功能。

## ✨ 核心特性

### 🎯 主要功能
- **关键词搜索**: 根据关键词批量获取YouTube视频URL
- **批量下载**: 自动下载所有视频的评论，无需YouTube API
- **多格式保存**: 支持JSON、CSV、TXT格式输出
- **智能重试**: 自动处理下载失败和网络错误
- **交互式界面**: 友好的命令行交互体验

### 📊 输出格式
- **视频信息**: JSON/CSV格式保存视频元数据
- **评论数据**: 包含评论内容、作者、时间、点赞数等完整信息
- **详细日志**: 完整的下载过程记录和错误日志

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/CaoZhiGordon/youtube_comment_crawl.git
cd youtube_comment_crawl

# 安装依赖
pip install -r requirements.txt
```

### 2. 基础使用

#### 方式一：完整批量处理（推荐）
```bash
python batch_comment_downloader.py
```

#### 方式二：简化版本（无selenium）
```bash
python simple_batch_downloader.py
```

#### 方式三：仅URL爬取
```bash
python url.py
```

### 3. 演示测试
```bash
python demo_batch.py
```

## 📁 项目结构

```
youtube_comment_crawl/
├── 📂 youtube_comment_downloader/    # 核心评论下载包
│   ├── __init__.py                   # 主入口和CLI接口
│   ├── downloader.py                 # 评论下载核心逻辑
│   └── __main__.py                   # 命令行入口
├── 📄 batch_comment_downloader.py    # 完整批量下载工具 (推荐)
├── 📄 simple_batch_downloader.py     # 简化版批量工具
├── 📄 url.py                         # URL批量爬取工具
├── 📄 demo_batch.py                  # 演示脚本
├── 📂 batch_comments_output/         # 输出目录
│   ├── urls/                         # 视频URL文件
│   ├── comments/                     # 评论JSON文件
│   └── logs/                         # 下载日志
└── 📚 文档文件
    ├── BATCH_USAGE.md               # 详细使用指南
    ├── CSV_BATCH_README.md          # CSV批处理说明
    └── SIMPLE_BATCH_README.md       # 简化版说明
```

## 🎮 使用模式

### 模式1: 完整流程 (推荐)
1. 🔍 输入搜索关键词（支持多个关键词，逗号分隔）
2. ⚙️ 设置URL搜索参数（每个关键词最大视频数、滚动次数等）
3. 📥 自动获取视频URL并保存
4. 🔧 设置评论下载参数（数量限制、排序方式、语言等）
5. ⬇️ 批量下载所有视频的评论

### 模式2: 仅搜索URL
- 只获取和保存视频URL，不下载评论
- 适合先收集URL，后续再下载

### 模式3: 从文件批量下载
- 从已有的URL文件批量下载评论
- 支持JSON、CSV、TXT格式的URL文件

## ⚙️ 参数配置

### URL搜索参数
- **关键词**: 搜索的关键词（支持中文）
- **每个关键词最大视频数**: 默认20个
- **页面滚动次数**: 默认5次（影响获取的视频数量）

### 评论下载参数
- **评论数量限制**: 每个视频下载的评论数量，默认100
- **排序方式**: 
  - `0` = 热门评论优先
  - `1` = 最新评论优先（默认）
- **语言设置**: 如 `zh`(中文)、`en`(英文)，默认自动
- **格式化输出**: 是否格式化JSON，默认是
- **下载间隔**: 视频间下载间隔秒数，默认2秒

## 📝 使用示例

### 示例1: 搜索AI相关视频
```python
# 运行 batch_comment_downloader.py 后的交互示例
关键词: 人工智能,ChatGPT,机器学习
每个关键词最大视频数: 30
页面滚动次数: 8
评论数量限制: 200
排序方式: 1 (最新)
语言设置: zh
```

### 示例2: 从文件批量处理
```bash
# 准备URL文件 (每行一个URL)
echo "https://www.youtube.com/watch?v=VIDEO_ID1" > urls.txt
echo "https://www.youtube.com/watch?v=VIDEO_ID2" >> urls.txt

# 运行程序，选择模式3，导入文件
python batch_comment_downloader.py
```

### 示例3: 作为Python库使用
```python
from youtube_comment_downloader import YoutubeCommentDownloader
from itertools import islice

# 下载单个视频的评论
downloader = YoutubeCommentDownloader()
comments = downloader.get_comments_from_url(
    'https://www.youtube.com/watch?v=ScMzIvxBSi4', 
    sort_by=1  # 最新评论
)

# 打印前10条评论
for comment in islice(comments, 10):
    print(f"作者: {comment['author']}")
    print(f"内容: {comment['text']}")
    print(f"时间: {comment['time']}")
    print("-" * 50)
```

## 🔧 高级功能

### 自动重试机制
- 下载失败的视频会记录在日志中
- 支持根据失败日志重新处理

### 智能文件命名
- 视频文件以"视频ID_标题"命名
- 自动处理特殊字符，确保文件名有效

### 详细统计报告
- URL获取统计（关键词、视频类型分布）
- 评论下载统计（成功率、失败原因）
- 完整的时间和性能记录

## ⚠️ 注意事项

### 使用限制
1. **请合理使用**: 避免过于频繁的请求
2. **遵守YouTube政策**: 仅用于合法的研究和分析
3. **网络稳定性**: 建议在稳定的网络环境下使用

### 常见问题
1. **Chrome驱动问题**: 程序会自动下载Chrome驱动
2. **网络超时**: 可以调整timeout参数
3. **内存占用**: 大量视频处理时注意内存使用

### 性能优化
- 使用无头浏览器模式 (`headless=True`)
- 禁用图片和CSS加载
- 合理设置下载间隔避免被限制

## 📦 依赖包

### 核心依赖
- `youtube-comment-downloader`: 评论下载核心包
- `requests`: HTTP请求库
- `dateparser`: 日期解析库

### 批量处理依赖
- `selenium`: Web自动化（完整版需要）
- `webdriver-manager`: Chrome驱动管理
- `beautifulsoup4`: HTML解析
- `pandas`: 数据处理

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目使用 [MIT许可证](LICENSE)。

## 🙏 致谢

- 感谢 [egbertbouman/youtube-comment-downloader](https://github.com/egbertbouman/youtube-comment-downloader) 提供的核心评论下载功能
- 基于该项目构建了批量处理和URL爬取功能

## 📊 输出文件说明

### URL文件
- `video_urls_TIMESTAMP.json`: 完整的视频信息（推荐）
- `video_urls_TIMESTAMP.csv`: 表格格式，便于Excel处理
- `urls_only_TIMESTAMP.txt`: 纯URL列表

### 评论文件
- `VIDEOID_TITLE.json`: 每个视频的评论数据
- 包含评论内容、作者、时间、点赞数等完整信息

### 日志文件
- `download_log_TIMESTAMP.txt`: 详细的下载日志
- 包含成功/失败状态、耗时、错误信息等

---

**开始使用**: 运行 `python batch_comment_downloader.py` 并按照交互式提示操作即可！🎉