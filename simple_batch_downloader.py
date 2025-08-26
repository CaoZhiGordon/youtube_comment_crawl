#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版批量YouTube评论下载工具
不依赖selenium，通过手动输入URL列表或从文件读取进行批量下载
"""

import os
import sys
import time
import json
import csv
import subprocess
from datetime import datetime


class SimpleBatchDownloader:
    def __init__(self, output_dir="simple_batch_output"):
        """
        初始化简化版批量下载器
        
        Args:
            output_dir (str): 输出目录
        """
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 创建子目录
        self.comments_dir = os.path.join(output_dir, "comments")
        self.logs_dir = os.path.join(output_dir, "logs")
        
        for dir_path in [self.comments_dir, self.logs_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
        print(f"🚀 简化版批量评论下载器初始化完成")
        print(f"📁 输出目录: {output_dir}")
        print(f"  📂 评论目录: {self.comments_dir}")
        print(f"  📂 日志目录: {self.logs_dir}")

    def extract_video_id(self, url):
        """从YouTube URL中提取视频ID"""
        try:
            if "watch?v=" in url:
                return url.split("watch?v=")[1].split("&")[0]
            elif "/shorts/" in url:
                return url.split("/shorts/")[1].split("?")[0]
            elif "youtu.be/" in url:
                return url.split("youtu.be/")[1].split("?")[0]
            else:
                return "unknown"
        except:
            return "unknown"

    def extract_video_info_from_url(self, url, index=1):
        """从URL提取基本视频信息"""
        video_id = self.extract_video_id(url)
        video_type = "shorts" if "/shorts/" in url else "watch"
        
        return {
            "序号": index,
            "标题": f"Video_{video_id}",
            "URL": url,
            "视频ID": video_id,
            "类型": video_type,
            "关键词": "手动输入",
            "获取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def download_comments_for_video(self, video_info, limit=100, sort=1, language=None, pretty=True):
        """
        为单个视频下载评论
        
        Args:
            video_info (dict): 视频信息
            limit (int): 评论数量限制
            sort (int): 排序方式 (0=热门, 1=最新)
            language (str): 语言设置
            pretty (bool): 是否格式化JSON
            
        Returns:
            tuple: (是否成功, 输出文件路径)
        """
        video_id = video_info.get('视频ID', 'unknown')
        video_title = video_info.get('标题', 'unknown')
        
        if video_id == 'unknown':
            print(f"❌ 无效的视频ID: {video_title}")
            return False, None
            
        # 生成输出文件名
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        output_filename = f"{video_id}_{safe_title}.json"
        output_path = os.path.join(self.comments_dir, output_filename)
        
        # 构建命令
        cmd = [
            sys.executable, "-m", "youtube_comment_downloader",
            "--youtubeid", video_id,
            "--output", output_path,
            "--limit", str(limit),
            "--sort", str(sort)
        ]
        
        if language:
            cmd.extend(["--language", language])
            
        if pretty:
            cmd.append("--pretty")
        
        try:
            print(f"⬇️ 正在下载评论: {video_title[:50]}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ 评论下载成功: {output_filename}")
                return True, output_path
            else:
                print(f"❌ 评论下载失败: {video_title}")
                print(f"错误信息: {result.stderr}")
                return False, None
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 下载超时: {video_title}")
            return False, None
        except Exception as e:
            print(f"❌ 下载出错: {e}")
            return False, None

    def batch_download_comments(self, video_list, limit=100, sort=1, language=None, pretty=True, delay=2):
        """
        批量下载评论
        
        Args:
            video_list (list): 视频信息列表
            limit (int): 每个视频的评论数量限制
            sort (int): 排序方式
            language (str): 语言设置
            pretty (bool): 是否格式化JSON
            delay (int): 下载间隔秒数
            
        Returns:
            dict: 下载结果统计
        """
        print(f"\n🚀 开始批量下载 {len(video_list)} 个视频的评论")
        
        success_count = 0
        failed_count = 0
        failed_videos = []
        
        # 创建下载日志
        log_file = os.path.join(self.logs_dir, f"download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"批量下载开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"总视频数: {len(video_list)}\n")
            log.write(f"参数设置: limit={limit}, sort={sort}, language={language}, pretty={pretty}\n")
            log.write("="*80 + "\n\n")
            
            for i, video_info in enumerate(video_list, 1):
                print(f"\n{'='*60}")
                print(f"正在处理第 {i}/{len(video_list)} 个视频")
                
                start_time = time.time()
                success, output_path = self.download_comments_for_video(
                    video_info, limit, sort, language, pretty
                )
                end_time = time.time()
                
                # 记录日志
                log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                log_entry += f"视频 {i}/{len(video_list)}: {video_info.get('标题', 'unknown')[:50]}\n"
                log_entry += f"视频ID: {video_info.get('视频ID', 'unknown')}\n"
                log_entry += f"URL: {video_info.get('URL', 'unknown')}\n"
                
                if success:
                    success_count += 1
                    log_entry += f"状态: ✅ 成功\n"
                    log_entry += f"输出文件: {output_path}\n"
                else:
                    failed_count += 1
                    failed_videos.append(video_info)
                    log_entry += f"状态: ❌ 失败\n"
                
                log_entry += f"耗时: {end_time - start_time:.2f}秒\n"
                log_entry += "-" * 80 + "\n\n"
                
                log.write(log_entry)
                log.flush()
                
                # 添加延迟
                if i < len(video_list) and delay > 0:
                    print(f"⏱️ 等待 {delay} 秒后继续...")
                    time.sleep(delay)
            
            # 写入最终统计
            log.write(f"\n批量下载完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"成功下载: {success_count} 个\n")
            log.write(f"下载失败: {failed_count} 个\n")
            log.write(f"成功率: {success_count/len(video_list)*100:.1f}%\n")
        
        result = {
            "总数": len(video_list),
            "成功": success_count,
            "失败": failed_count,
            "成功率": f"{success_count/len(video_list)*100:.1f}%",
            "失败视频": failed_videos,
            "日志文件": log_file
        }
        
        print(f"\n🎊 批量下载完成!")
        print(f"📊 成功: {success_count}, 失败: {failed_count}, 成功率: {result['成功率']}")
        print(f"📋 详细日志: {log_file}")
        
        return result

    def save_video_list_to_file(self, video_list, filename=None):
        """保存视频列表到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_list_{timestamp}.json"
            
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(video_list, f, ensure_ascii=False, indent=2)
            
        print(f"💾 视频列表已保存: {filepath}")
        return filepath

    def load_video_list_from_file(self, filepath):
        """从文件加载视频列表"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
            
        video_list = []
        
        if filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    video_list = data
                elif isinstance(data, dict) and 'videos' in data:
                    video_list = data['videos']
                else:
                    raise ValueError("JSON文件格式不正确")
                    
        elif filepath.endswith('.csv'):
            import pandas as pd
            df = pd.read_csv(filepath)
            video_list = df.to_dict('records')
            
        elif filepath.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                for i, url in enumerate(urls):
                    video_list.append(self.extract_video_info_from_url(url, i + 1))
        else:
            raise ValueError("不支持的文件格式，请使用 .json, .csv 或 .txt 文件")
            
        return video_list

    def generate_report(self, download_results):
        """生成下载报告"""
        print(f"\n{'='*60}")
        print("📊 批量下载结果报告")
        print(f"{'='*60}")
        
        print("⬇️ 评论下载结果:")
        print(f"   📊 总视频数: {download_results['总数']}")
        print(f"   ✅ 成功下载: {download_results['成功']}")
        print(f"   ❌ 下载失败: {download_results['失败']}")
        print(f"   📈 成功率: {download_results['成功率']}")
        print(f"   📋 日志文件: {download_results['日志文件']}")
        
        if download_results['失败'] > 0:
            print(f"\n❌ 失败的视频:")
            for video in download_results['失败视频']:
                print(f"   - {video.get('标题', 'unknown')} ({video.get('视频ID', 'unknown')})")
        
        print(f"{'='*60}")


def main():
    """主函数"""
    print("🎬 简化版批量YouTube评论下载工具")
    print("=" * 60)
    
    # 初始化下载器
    downloader = SimpleBatchDownloader("simple_batch_output")
    
    while True:
        print(f"\n{'='*60}")
        print("请选择操作模式:")
        print("1. 手动输入视频URL批量下载")
        print("2. 从文件读取URL批量下载")
        print("3. 单个视频URL下载")
        print("4. 退出")
        print("=" * 60)
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == '1':
            # 手动输入URL
            print("\n请输入YouTube视频URL (每行一个，输入空行结束):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                if 'youtube.com' in url or 'youtu.be' in url:
                    urls.append(url)
                else:
                    print("⚠️ 请输入有效的YouTube URL")
            
            if not urls:
                print("❌ 至少需要一个URL")
                continue
                
            # 转换为视频信息列表
            video_list = []
            for i, url in enumerate(urls):
                video_info = downloader.extract_video_info_from_url(url, i + 1)
                video_list.append(video_info)
            
            print(f"✅ 共输入 {len(video_list)} 个视频URL")
            
            # 保存视频列表
            downloader.save_video_list_to_file(video_list)
            
        elif choice == '2':
            # 从文件读取
            filepath = input("请输入文件路径 (.json/.csv/.txt): ").strip()
            
            try:
                video_list = downloader.load_video_list_from_file(filepath)
                print(f"✅ 从文件中读取到 {len(video_list)} 个视频")
            except Exception as e:
                print(f"❌ 读取文件失败: {e}")
                continue
                
        elif choice == '3':
            # 单个视频
            url = input("请输入YouTube视频URL: ").strip()
            if not url or 'youtube.com' not in url and 'youtu.be' not in url:
                print("❌ 请输入有效的YouTube URL")
                continue
                
            video_info = downloader.extract_video_info_from_url(url)
            video_list = [video_info]
            
        elif choice == '4':
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重试")
            continue
        
        if choice in ['1', '2', '3']:
            # 评论下载参数设置
            print(f"\n⚙️ 设置下载参数:")
            
            try:
                limit = int(input("每个视频评论数量限制 (默认100): ").strip() or "100")
            except:
                limit = 100
            
            sort_choice = input("排序方式 (0=热门, 1=最新, 默认1): ").strip() or "1"
            sort = int(sort_choice) if sort_choice in ['0', '1'] else 1
            
            language = input("语言设置 (如: zh, en, 默认自动): ").strip() or None
            
            pretty_choice = input("格式化JSON输出 (y/n, 默认y): ").strip().lower()
            pretty = pretty_choice != 'n'
            
            try:
                delay = int(input("下载间隔秒数 (默认2): ").strip() or "2")
            except:
                delay = 2
            
            # 批量下载评论
            download_results = downloader.batch_download_comments(
                video_list, limit, sort, language, pretty, delay
            )
            
            # 生成报告
            downloader.generate_report(download_results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序出现错误: {e}") 