# 🎬 简化版批量YouTube评论下载工具

这是一个轻量级的批量YouTube评论下载工具，**无需安装selenium**，通过手动输入URL或从文件读取URL进行批量下载。

## ✨ 特点

- **轻量级**: 不依赖selenium和浏览器驱动
- **简单易用**: 支持手动输入URL或从文件读取
- **批量处理**: 可以同时处理多个视频
- **详细日志**: 完整的下载日志和错误记录
- **多格式支持**: 支持从JSON、CSV、TXT文件读取URL
- **交互式配置**: 所有参数都可以交互式设置

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 直接运行

```bash
python3 simple_batch_downloader.py
```

## 📋 使用模式

### 模式1: 手动输入URL批量下载
1. 选择模式1
2. 逐行输入YouTube视频URL
3. 输入空行结束
4. 设置下载参数
5. 开始批量下载

### 模式2: 从文件读取URL批量下载  
1. 准备URL文件 (支持.json/.csv/.txt格式)
2. 选择模式2
3. 输入文件路径
4. 设置下载参数
5. 开始批量下载

### 模式3: 单个视频URL下载
1. 选择模式3  
2. 输入单个YouTube视频URL
3. 设置下载参数
4. 开始下载

## 📁 支持的文件格式

### TXT格式 (推荐，最简单)
```
# 这是注释，会被忽略
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.youtube.com/watch?v=VIDEO_ID2
https://youtu.be/VIDEO_ID3
```

### JSON格式
```json
[
  {
    "序号": 1,
    "标题": "视频标题",
    "URL": "https://www.youtube.com/watch?v=VIDEO_ID",
    "视频ID": "VIDEO_ID",
    "类型": "watch"
  }
]
```

### CSV格式
包含URL列的CSV文件，支持Excel导出的格式。

## ⚙️ 参数配置

### 下载参数
- **评论数量限制**: 每个视频下载的评论数量 (默认100)
- **排序方式**: 
  - 0 = 热门评论优先
  - 1 = 最新评论优先 (默认)
- **语言设置**: 如 zh(中文)、en(英文)，默认自动检测
- **格式化输出**: 是否格式化JSON输出 (默认是)
- **下载间隔**: 视频间下载间隔秒数 (默认2秒，避免被限制)

## 📊 输出结构

```
simple_batch_output/
├── comments/                    # 评论JSON文件
│   ├── VIDEO_ID1_Title.json
│   └── VIDEO_ID2_Title.json
├── logs/                        # 下载日志
│   └── download_log_TIMESTAMP.txt
└── video_list_TIMESTAMP.json   # 视频列表备份
```

## 🎯 使用示例

### 示例1: 从TXT文件批量下载

1. 创建 `my_videos.txt` 文件:
```
https://www.youtube.com/watch?v=4o3qbZMkr-M
https://www.youtube.com/watch?v=ScMzIvxBSi4
```

2. 运行程序:
```bash
python3 simple_batch_downloader.py
```

3. 选择模式2，输入文件路径 `my_videos.txt`

4. 设置参数 (示例):
```
每个视频评论数量限制: 50
排序方式: 1 (最新)
语言设置: zh
格式化JSON输出: y
下载间隔秒数: 3
```

### 示例2: 手动输入URL

1. 运行程序，选择模式1
2. 逐行输入URL:
```
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.youtube.com/watch?v=VIDEO_ID2
[空行结束]
```
3. 设置参数并开始下载

## 📈 功能特性

### ✅ 已实现
- [x] 批量下载多个视频的评论
- [x] 支持多种URL文件格式 (TXT/JSON/CSV)
- [x] 详细的下载日志和错误记录
- [x] 交互式参数配置
- [x] 自动文件命名和组织
- [x] 下载进度显示
- [x] 成功率统计和报告生成

### 🔄 相比完整版的差异
- **简化**: 不包含自动搜索功能 (需要手动提供URL)
- **轻量**: 不依赖selenium和浏览器驱动
- **稳定**: 减少了外部依赖，更加可靠

## 🚨 注意事项

### 使用建议
1. **合理使用**: 设置适当的下载间隔，避免过于频繁的请求
2. **遵守政策**: 仅用于合法的研究和分析目的
3. **网络稳定**: 确保网络连接稳定，避免下载中断

### 常见问题
1. **URL格式**: 确保输入的是有效的YouTube URL
2. **文件路径**: 使用绝对路径或确保文件在当前目录
3. **权限问题**: 确保有写入输出目录的权限

## 🛠️ 高级用法

### 批处理脚本
创建自动化脚本:
```python
from simple_batch_downloader import SimpleBatchDownloader

downloader = SimpleBatchDownloader("my_output")
video_list = downloader.load_video_list_from_file("urls.txt")
results = downloader.batch_download_comments(
    video_list, limit=100, sort=1, delay=2
)
```

### 自定义配置
```python
# 自定义输出目录和参数
downloader = SimpleBatchDownloader("custom_output")

# 高质量下载配置
results = downloader.batch_download_comments(
    video_list,
    limit=500,     # 更多评论
    sort=0,        # 热门评论
    language="zh", # 中文
    pretty=True,   # 格式化
    delay=5        # 更长间隔
)
```

## 🎉 开始使用

1. **安装依赖**: 
   ```bash
   pip install -r requirements.txt
   ```

2. **开始使用**:
   ```bash
   python3 simple_batch_downloader.py
   ```

3. **查看结果**: 检查 `simple_batch_output/` 目录

---

**提示**: 这个简化版工具专注于批量下载功能，如果你需要自动搜索YouTube视频URL的功能，请使用完整版的 `batch_comment_downloader.py` (需要安装selenium)。 