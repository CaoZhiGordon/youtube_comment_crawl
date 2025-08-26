#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量YouTube评论下载工具
先根据关键词批量获取视频URL，然后批量下载评论
整合了URL爬取和评论下载功能
"""

import os
import sys
import time
import json
import csv
import requests
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd


class BatchCommentDownloader:
    def __init__(self, output_dir="batch_comments", headless=True, timeout=30):
        """
        初始化批量评论下载器
        
        Args:
            output_dir (str): 输出目录
            headless (bool): 是否无头模式运行
            timeout (int): 超时时间
        """
        self.output_dir = output_dir
        self.headless = headless
        self.timeout = timeout
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 创建子目录
        self.urls_dir = os.path.join(output_dir, "urls")
        self.comments_dir = os.path.join(output_dir, "comments")
        self.logs_dir = os.path.join(output_dir, "logs")
        
        for dir_path in [self.urls_dir, self.comments_dir, self.logs_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
        print(f"🚀 批量评论下载器初始化完成")
        print(f"📁 输出目录: {output_dir}")
        print(f"  📂 URL目录: {self.urls_dir}")
        print(f"  📂 评论目录: {self.comments_dir}")
        print(f"  📂 日志目录: {self.logs_dir}")
        print(f"🤖 无头模式: {'开启' if headless else '关闭'}")

    def get_chrome_driver(self):
        """获取Chrome WebDriver"""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
            
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # 禁用图片和CSS加载以提高速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(self.timeout)
            return driver
        except Exception as e:
            print(f"❌ Chrome驱动初始化失败: {e}")
            raise

    def get_urls_from_keyword(self, keyword, max_results=40, scroll_times=5):
        """
        根据关键词获取视频URLs
        
        Args:
            keyword (str): 搜索关键词
            max_results (int): 最大结果数量
            scroll_times (int): 滚动次数
            
        Returns:
            list: 包含视频信息的字典列表
        """
        print(f"\n🔍 开始搜索关键词: '{keyword}'")
        
        # URL编码
        search_keyword_encode = requests.utils.quote(keyword)
        search_url = f"https://www.youtube.com/results?search_query={search_keyword_encode}"
        
        driver = self.get_chrome_driver()
        video_list = []
        
        try:
            # 访问搜索页面
            driver.get(search_url)
            print("📄 搜索页面已加载，正在获取搜索结果...")
            time.sleep(3)
            
            # 滚动加载更多结果
            for i in range(scroll_times):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                print(f"🔄 搜索结果加载中... ({i+1}/{scroll_times})")
            
            # 获取页面源码
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'lxml')
            
            # 查找所有视频链接
            video_elements = soup.select("a#video-title")
            
            print(f"✅ 找到 {len(video_elements)} 个视频")
            
            for idx, element in enumerate(video_elements[:max_results]):
                try:
                    title = element.text.strip()
                    href = element.get('href')
                    
                    if href and title:
                        # 构建完整URL
                        if href.startswith('/'):
                            video_url = f"https://www.youtube.com{href}"
                        else:
                            video_url = href
                        
                        # 提取视频ID
                        video_id = self.extract_video_id(video_url)
                        
                        # 判断视频类型
                        video_type = "shorts" if "/shorts/" in video_url else "watch"
                        
                        video_info = {
                            "序号": idx + 1,
                            "标题": title,
                            "URL": video_url,
                            "视频ID": video_id,
                            "类型": video_type,
                            "关键词": keyword,
                            "获取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        video_list.append(video_info)
                        print(f"  {idx+1}. {title[:50]}...")
                        
                except Exception as e:
                    print(f"⚠️ 解析视频信息时出错: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ 搜索过程中出错: {e}")
        finally:
            driver.quit()
            
        print(f"🎉 完成! 共获取到 {len(video_list)} 个视频URL")
        return video_list

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

    def batch_search_keywords(self, keywords, max_results_per_keyword=40, scroll_times=5):
        """
        批量搜索多个关键词
        
        Args:
            keywords (list): 关键词列表
            max_results_per_keyword (int): 每个关键词的最大结果数
            scroll_times (int): 滚动次数
            
        Returns:
            dict: 按关键词分组的结果
        """
        print(f"\n🚀 开始批量搜索 {len(keywords)} 个关键词")
        
        all_results = {}
        total_videos = 0
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n{'='*60}")
            print(f"正在处理第 {i}/{len(keywords)} 个关键词")
            
            try:
                video_list = self.get_urls_from_keyword(
                    keyword=keyword,
                    max_results=max_results_per_keyword,
                    scroll_times=scroll_times
                )
                
                all_results[keyword] = video_list
                total_videos += len(video_list)
                
                # 添加延迟避免被封
                if i < len(keywords):
                    print("⏱️ 等待5秒后继续...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"❌ 关键词 '{keyword}' 搜索失败: {e}")
                all_results[keyword] = []
                
        print(f"\n🎊 批量搜索完成! 总共获取 {total_videos} 个视频URL")
        return all_results

    def save_urls_to_files(self, results, timestamp=None):
        """保存URL结果到文件"""
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        # 保存JSON格式
        json_file = os.path.join(self.urls_dir, f"video_urls_{timestamp}.json")
        summary = {
            "总关键词数": len(results),
            "总视频数": sum(len(videos) for videos in results.values()),
            "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "关键词统计": {k: len(v) for k, v in results.items()}
        }
        
        output_data = {
            "统计信息": summary,
            "详细数据": results
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON文件已保存: {json_file}")
        
        # 保存CSV格式
        csv_file = os.path.join(self.urls_dir, f"video_urls_{timestamp}.csv")
        all_videos = []
        for keyword, videos in results.items():
            all_videos.extend(videos)
            
        if all_videos:
            df = pd.DataFrame(all_videos)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"💾 CSV文件已保存: {csv_file}")
        
        # 保存纯URL列表
        txt_file = os.path.join(self.urls_dir, f"urls_only_{timestamp}.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            for keyword, videos in results.items():
                f.write(f"# 关键词: {keyword}\n")
                for video in videos:
                    f.write(f"{video['URL']}\n")
                f.write("\n")
        print(f"💾 URL列表已保存: {txt_file}")
        
        return json_file, csv_file, txt_file

    def download_comments_for_video(self, video_info, limit=1000, sort=1, language=None, output_format='csv'):
        """
        为单个视频下载评论
        
        Args:
            video_info (dict): 视频信息
            limit (int): 评论数量限制
            sort (int): 排序方式 (0=热门, 1=最新)
            language (str): 语言设置
            output_format (str): 输出格式 ('csv' 或 'json')
            
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
        
        # 先下载为JSON格式（临时文件）
        temp_json_filename = f"{video_id}_{safe_title}_temp.json"
        temp_json_path = os.path.join(self.comments_dir, temp_json_filename)
        
        # 最终输出文件
        if output_format.lower() == 'csv':
            final_filename = f"{video_id}_{safe_title}.csv"
        else:
            final_filename = f"{video_id}_{safe_title}.json"
        final_output_path = os.path.join(self.comments_dir, final_filename)
        
        # 构建命令
        cmd = [
            sys.executable, "-m", "youtube_comment_downloader",
            "--youtubeid", video_id,
            "--output", temp_json_path,
            "--limit", str(limit),
            "--sort", str(sort),
            "--pretty"
        ]
        
        if language:
            cmd.extend(["--language", language])
        
        try:
            print(f"⬇️ 正在下载评论: {video_title[:50]}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # 如果要求CSV格式，转换JSON到CSV
                if output_format.lower() == 'csv':
                    success = self.convert_json_to_csv(temp_json_path, final_output_path, video_info)
                    # 删除临时JSON文件
                    if os.path.exists(temp_json_path):
                        os.remove(temp_json_path)
                    
                    if success:
                        print(f"✅ 评论下载并转换成功: {final_filename}")
                        return True, final_output_path
                    else:
                        print(f"❌ CSV转换失败: {video_title}")
                        return False, None
                else:
                    # JSON格式，直接重命名
                    if os.path.exists(temp_json_path):
                        os.rename(temp_json_path, final_output_path)
                    print(f"✅ 评论下载成功: {final_filename}")
                    return True, final_output_path
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

    def convert_json_to_csv(self, json_path, csv_path, video_info):
        """
        将JSON格式的评论转换为CSV格式
        
        Args:
            json_path (str): JSON文件路径
            csv_path (str): CSV输出路径
            video_info (dict): 视频信息
            
        Returns:
            bool: 转换是否成功
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试修复不完整的JSON
            content = content.strip()
            if not content.endswith('}') and not content.endswith(']'):
                # 可能是不完整的JSON，尝试修复
                if '"comments": [' in content:
                    # 找到最后一个完整的评论对象
                    last_brace = content.rfind('},')
                    if last_brace != -1:
                        content = content[:last_brace+1] + '\n    ]\n}'
                        print("⚠️ 检测到不完整的JSON文件，尝试自动修复")
            
            data = json.loads(content)
            
            # 处理JSON结构：可能是直接的数组，也可能是包含comments字段的对象
            if isinstance(data, dict) and 'comments' in data:
                comments_data = data['comments']
            elif isinstance(data, list):
                comments_data = data
            else:
                print(f"❌ 不支持的JSON格式: {type(data)}")
                return False
            
            # 准备CSV数据
            csv_data = []
            
            for comment in comments_data:
                if not isinstance(comment, dict):
                    print(f"⚠️ 跳过无效评论数据: {type(comment)}")
                    continue
                    
                # 处理数值字段
                votes = comment.get('votes', 0)
                if isinstance(votes, str):
                    # 移除逗号并转换为数字
                    votes = int(votes.replace(',', '')) if votes.replace(',', '').isdigit() else 0
                
                replies = comment.get('replies', 0)
                if isinstance(replies, str):
                    replies = int(replies) if replies.isdigit() else 0
                
                # 提取评论信息
                row = {
                    '视频ID': video_info.get('视频ID', ''),
                    '视频标题': video_info.get('标题', ''),
                    '视频URL': video_info.get('URL', ''),
                    '评论ID': comment.get('cid', ''),
                    '评论内容': comment.get('text', ''),
                    '作者': comment.get('author', ''),
                    '作者频道ID': comment.get('channel', ''),
                    '点赞数': votes,
                    '回复数': replies,
                    '发布时间': comment.get('time', ''),
                    '发布时间戳': comment.get('time_parsed', ''),
                    '是否置顶': comment.get('pinned', False),
                    '是否作者回复': comment.get('author_is_uploader', False),
                    '照片URL': comment.get('photo', ''),
                    '是否有心形标记': comment.get('heart', False)
                }
                csv_data.append(row)
            
            # 写入CSV文件
            if csv_data:
                df = pd.DataFrame(csv_data)
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"📊 成功转换 {len(csv_data)} 条评论到CSV格式")
                return True
            else:
                print("⚠️ 没有找到评论数据")
                return False
                
        except Exception as e:
            print(f"❌ JSON到CSV转换失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def batch_download_comments(self, video_list, limit=1000, sort=1, language=None, output_format='csv', delay=2):
        """
        批量下载评论
        
        Args:
            video_list (list): 视频信息列表
            limit (int): 每个视频的评论数量限制
            sort (int): 排序方式
            language (str): 语言设置
            output_format (str): 输出格式 ('csv' 或 'json')
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
            log.write(f"参数设置: limit={limit}, sort={sort}, language={language}, output_format={output_format}\n")
            log.write("="*80 + "\n\n")
            
            for i, video_info in enumerate(video_list, 1):
                print(f"\n{'='*60}")
                print(f"正在处理第 {i}/{len(video_list)} 个视频")
                
                start_time = time.time()
                success, output_path = self.download_comments_for_video(
                    video_info, limit, sort, language, output_format
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

    def batch_download_comments_by_keyword(self, keyword_results, limit=1000, sort=1, language=None, output_format='csv', delay=2):
        """
        按关键词批量下载评论并合并到单个文件
        
        Args:
            keyword_results (dict): 按关键词分组的视频列表
            limit (int): 每个视频的评论数量限制
            sort (int): 排序方式
            language (str): 语言设置
            output_format (str): 输出格式 ('csv' 或 'json')
            delay (int): 下载间隔秒数
            
        Returns:
            dict: 下载结果统计
        """
        print(f"\n🚀 开始按关键词批量下载评论")
        
        total_keywords = len(keyword_results)
        total_videos = sum(len(videos) for videos in keyword_results.values())
        success_count = 0
        failed_count = 0
        failed_videos = []
        keyword_results_summary = {}
        
        # 创建下载日志
        log_file = os.path.join(self.logs_dir, f"download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"批量下载开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"总关键词数: {total_keywords}\n")
            log.write(f"总视频数: {total_videos}\n")
            log.write(f"参数设置: limit={limit}, sort={sort}, language={language}, output_format={output_format}\n")
            log.write("="*80 + "\n\n")
            
            for keyword_idx, (keyword, video_list) in enumerate(keyword_results.items(), 1):
                print(f"\n{'='*80}")
                print(f"正在处理关键词 {keyword_idx}/{total_keywords}: '{keyword}'")
                print(f"该关键词下有 {len(video_list)} 个视频")
                
                # 为当前关键词创建合并的评论数据
                all_comments_data = []
                keyword_success = 0
                keyword_failed = 0
                
                log.write(f"关键词 {keyword_idx}/{total_keywords}: {keyword}\n")
                log.write(f"视频数量: {len(video_list)}\n")
                log.write("-" * 40 + "\n")
                
                for video_idx, video_info in enumerate(video_list, 1):
                    print(f"\n正在处理第 {video_idx}/{len(video_list)} 个视频")
                    
                    video_id = video_info.get('视频ID', 'unknown')
                    video_title = video_info.get('标题', 'unknown')
                    
                    if video_id == 'unknown':
                        print(f"❌ 无效的视频ID: {video_title}")
                        failed_count += 1
                        keyword_failed += 1
                        failed_videos.append(video_info)
                        continue
                    
                    # 临时JSON文件
                    temp_json_filename = f"temp_{video_id}.json"
                    temp_json_path = os.path.join(self.comments_dir, temp_json_filename)
                    
                    # 构建下载命令
                    cmd = [
                        sys.executable, "-m", "youtube_comment_downloader",
                        "--youtubeid", video_id,
                        "--output", temp_json_path,
                        "--limit", str(limit),
                        "--sort", str(sort),
                        "--pretty"
                    ]
                    
                    if language:
                        cmd.extend(["--language", language])
                    
                    try:
                        print(f"⬇️ 正在下载评论: {video_title[:50]}...")
                        start_time = time.time()
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                        end_time = time.time()
                        
                        if result.returncode == 0:
                            # 读取并解析JSON数据
                            comments = self.parse_comments_from_json(temp_json_path, video_info)
                            if comments:
                                all_comments_data.extend(comments)
                                success_count += 1
                                keyword_success += 1
                                print(f"✅ 成功获取 {len(comments)} 条评论")
                                
                                # 记录日志
                                log.write(f"  视频 {video_idx}: ✅ {video_title[:50]} - {len(comments)}条评论 ({end_time-start_time:.2f}s)\n")
                            else:
                                failed_count += 1
                                keyword_failed += 1
                                failed_videos.append(video_info)
                                log.write(f"  视频 {video_idx}: ❌ {video_title[:50]} - 解析失败\n")
                            
                            # 删除临时文件
                            if os.path.exists(temp_json_path):
                                os.remove(temp_json_path)
                                
                        else:
                            print(f"❌ 评论下载失败: {video_title}")
                            print(f"错误信息: {result.stderr}")
                            failed_count += 1
                            keyword_failed += 1
                            failed_videos.append(video_info)
                            log.write(f"  视频 {video_idx}: ❌ {video_title[:50]} - 下载失败\n")
                            
                    except subprocess.TimeoutExpired:
                        print(f"⏰ 下载超时: {video_title}")
                        failed_count += 1
                        keyword_failed += 1
                        failed_videos.append(video_info)
                        log.write(f"  视频 {video_idx}: ⏰ {video_title[:50]} - 超时\n")
                    except Exception as e:
                        print(f"❌ 下载出错: {e}")
                        failed_count += 1
                        keyword_failed += 1
                        failed_videos.append(video_info)
                        log.write(f"  视频 {video_idx}: ❌ {video_title[:50]} - 异常: {e}\n")
                    
                    # 添加延迟
                    if video_idx < len(video_list) and delay > 0:
                        print(f"⏱️ 等待 {delay} 秒后继续...")
                        time.sleep(delay)
                
                # 保存当前关键词的合并评论文件
                if all_comments_data:
                    # 创建安全的文件名
                    safe_keyword = "".join(c for c in keyword if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')[:30]
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    if output_format.lower() == 'csv':
                        output_filename = f"comments_{safe_keyword}_{timestamp}.csv"
                        output_path = os.path.join(self.comments_dir, output_filename)
                        self.save_comments_to_csv(all_comments_data, output_path)
                        print(f"📊 关键词 '{keyword}' 的评论已保存到: {output_filename}")
                        print(f"   总评论数: {len(all_comments_data)}")
                    else:
                        output_filename = f"comments_{safe_keyword}_{timestamp}.json"
                        output_path = os.path.join(self.comments_dir, output_filename)
                        self.save_comments_to_json(all_comments_data, output_path)
                        print(f"📄 关键词 '{keyword}' 的评论已保存到: {output_filename}")
                        print(f"   总评论数: {len(all_comments_data)}")
                        
                    keyword_results_summary[keyword] = {
                        "总视频数": len(video_list),
                        "成功视频数": keyword_success,
                        "失败视频数": keyword_failed,
                        "总评论数": len(all_comments_data),
                        "输出文件": output_filename
                    }
                else:
                    print(f"⚠️ 关键词 '{keyword}' 没有获取到任何评论")
                    keyword_results_summary[keyword] = {
                        "总视频数": len(video_list),
                        "成功视频数": 0,
                        "失败视频数": len(video_list),
                        "总评论数": 0,
                        "输出文件": None
                    }
                
                log.write(f"关键词总结: 成功{keyword_success}个，失败{keyword_failed}个，评论{len(all_comments_data)}条\n")
                log.write("="*80 + "\n\n")
                
                # 关键词间延迟
                if keyword_idx < total_keywords and delay > 0:
                    print(f"⏱️ 关键词间等待 {delay} 秒...")
                    time.sleep(delay)
            
            # 写入最终统计
            log.write(f"\n批量下载完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"总成功视频: {success_count} 个\n")
            log.write(f"总失败视频: {failed_count} 个\n")
            log.write(f"总成功率: {success_count/total_videos*100:.1f}%\n")
        
        result = {
            "总关键词数": total_keywords,
            "总视频数": total_videos,
            "成功视频数": success_count,
            "失败视频数": failed_count,
            "成功率": f"{success_count/total_videos*100:.1f}%",
            "关键词详情": keyword_results_summary,
            "失败视频": failed_videos,
            "日志文件": log_file
        }
        
        print(f"\n🎊 批量下载完成!")
        print(f"📊 总体统计: 成功{success_count}个视频，失败{failed_count}个视频，成功率{result['成功率']}")
        print(f"📋 详细日志: {log_file}")
        
        return result
    
    def parse_comments_from_json(self, json_path, video_info):
        """
        从JSON文件解析评论数据
        
        Args:
            json_path (str): JSON文件路径
            video_info (dict): 视频信息
            
        Returns:
            list: 评论数据列表
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试修复不完整的JSON
            content = content.strip()
            if not content.endswith('}') and not content.endswith(']'):
                if '"comments": [' in content:
                    last_brace = content.rfind('},')
                    if last_brace != -1:
                        content = content[:last_brace+1] + '\n    ]\n}'
                        print("⚠️ 检测到不完整的JSON文件，尝试自动修复")
            
            data = json.loads(content)
            
            # 处理JSON结构
            if isinstance(data, dict) and 'comments' in data:
                comments_data = data['comments']
            elif isinstance(data, list):
                comments_data = data
            else:
                print(f"❌ 不支持的JSON格式: {type(data)}")
                return []
            
            # 转换为统一格式
            processed_comments = []
            for comment in comments_data:
                if not isinstance(comment, dict):
                    continue
                    
                # 处理数值字段
                votes = comment.get('votes', 0)
                if isinstance(votes, str):
                    votes = int(votes.replace(',', '')) if votes.replace(',', '').isdigit() else 0
                
                replies = comment.get('replies', 0)
                if isinstance(replies, str):
                    replies = int(replies) if replies.isdigit() else 0
                
                # 创建评论记录
                comment_record = {
                    '视频ID': video_info.get('视频ID', ''),
                    '视频标题': video_info.get('标题', ''),
                    '视频URL': video_info.get('URL', ''),
                    '关键词': video_info.get('关键词', ''),
                    '评论ID': comment.get('cid', ''),
                    '评论内容': comment.get('text', ''),
                    '作者': comment.get('author', ''),
                    '作者频道ID': comment.get('channel', ''),
                    '点赞数': votes,
                    '回复数': replies,
                    '发布时间': comment.get('time', ''),
                    '发布时间戳': comment.get('time_parsed', ''),
                    '是否置顶': comment.get('pinned', False),
                    '是否作者回复': comment.get('author_is_uploader', False),
                    '照片URL': comment.get('photo', ''),
                    '是否有心形标记': comment.get('heart', False)
                }
                processed_comments.append(comment_record)
            
            return processed_comments
            
        except Exception as e:
            print(f"❌ 解析JSON文件失败: {e}")
            return []
    
    def save_comments_to_csv(self, comments_data, output_path):
        """保存评论数据到CSV文件"""
        try:
            if comments_data:
                df = pd.DataFrame(comments_data)
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                return True
            return False
        except Exception as e:
            print(f"❌ 保存CSV文件失败: {e}")
            return False
    
    def save_comments_to_json(self, comments_data, output_path):
        """保存评论数据到JSON文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(comments_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存JSON文件失败: {e}")
            return False

    def generate_report(self, url_results=None, download_results=None):
        """生成完整报告"""
        print(f"\n{'='*60}")
        print("📊 批量处理结果报告")
        print(f"{'='*60}")
        
        if url_results:
            print("🔍 URL获取结果:")
            total_videos = 0
            for keyword, videos in url_results.items():
                video_count = len(videos)
                total_videos += video_count
                
                # 统计视频类型
                watch_count = sum(1 for v in videos if v['类型'] == 'watch')
                shorts_count = sum(1 for v in videos if v['类型'] == 'shorts')
                
                print(f"   关键词: {keyword}")
                print(f"     📺 总视频数: {video_count}")
                print(f"     🎬 普通视频: {watch_count}")
                print(f"     📱 Shorts: {shorts_count}")
                
            print(f"   🎯 总计: {len(url_results)} 个关键词，{total_videos} 个视频\n")
        
        if download_results:
            print("⬇️ 评论下载结果:")
            if '总视频数' in download_results:  # 新格式
                print(f"   📊 总关键词数: {download_results['总关键词数']}")
                print(f"   📊 总视频数: {download_results['总视频数']}")
                print(f"   ✅ 成功下载: {download_results['成功视频数']}")
                print(f"   ❌ 下载失败: {download_results['失败视频数']}")
                print(f"   📈 成功率: {download_results['成功率']}")
                print(f"   📋 日志文件: {download_results['日志文件']}")
                
                # 显示每个关键词的详情
                if '关键词详情' in download_results:
                    print("\n   📂 关键词详情:")
                    for keyword, details in download_results['关键词详情'].items():
                        print(f"     🔖 {keyword}:")
                        print(f"       📺 视频: {details['成功视频数']}/{details['总视频数']}")
                        print(f"       💬 评论: {details['总评论数']}条")
                        if details['输出文件']:
                            print(f"       📄 文件: {details['输出文件']}")
            else:  # 旧格式兼容
                print(f"   📊 总视频数: {download_results.get('总数', 0)}")
                print(f"   ✅ 成功下载: {download_results.get('成功', 0)}")
                print(f"   ❌ 下载失败: {download_results.get('失败', 0)}")
                print(f"   📈 成功率: {download_results.get('成功率', '0%')}")
                print(f"   📋 日志文件: {download_results.get('日志文件', 'N/A')}")
        
        print(f"{'='*60}")


def main():
    """主函数"""
    print("🎬 批量YouTube评论下载工具")
    print("=" * 60)
    
    # 初始化下载器
    downloader = BatchCommentDownloader(
        output_dir="batch_comments_output",
        headless=True,  # 设置为False可以看到浏览器操作
        timeout=30
    )
    
    while True:
        print(f"\n{'='*60}")
        print("请选择操作模式:")
        print("1. 完整流程 (搜索URL + 下载评论)")
        print("2. 仅搜索并保存视频URL")
        print("3. 从已有URL文件批量下载评论")
        print("4. 退出")
        print("=" * 60)
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == '1':
            # 完整流程
            print("\n🔍 第一步: 获取视频URL")
            
            # 获取关键词
            print("请输入搜索关键词 (多个关键词请用逗号分隔):")
            keywords_input = input().strip()
            if not keywords_input:
                print("❌ 关键词不能为空")
                continue
            
            keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
            
            # URL搜索参数
            try:
                max_results = int(input("每个关键词最大视频数 (默认40): ").strip() or "40")
            except:
                max_results = 40
                
            try:
                scroll_times = int(input("页面滚动次数 (默认5): ").strip() or "5")
            except:
                scroll_times = 5
            
            # 搜索URL
            url_results = downloader.batch_search_keywords(keywords, max_results, scroll_times)
            
            if not any(url_results.values()):
                print("❌ 没有找到任何视频，程序结束")
                continue
            
            # 保存URL结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            downloader.save_urls_to_files(url_results, timestamp)
            
            # 准备下载评论
            print(f"\n⬇️ 第二步: 下载评论")
            
            # 合并所有视频
            all_videos = []
            for videos in url_results.values():
                all_videos.extend(videos)
            
            print(f"找到 {len(all_videos)} 个视频，准备下载评论")
            
            # 评论下载参数
            try:
                limit = int(input("每个视频评论数量限制 (默认1000): ").strip() or "1000")
            except:
                limit = 1000
            
            sort_choice = input("排序方式 (0=热门, 1=最新, 默认1): ").strip() or "1"
            sort = int(sort_choice) if sort_choice in ['0', '1'] else 1
            
            language = input("语言设置 (如: zh, en, 默认自动): ").strip() or None
            
            format_choice = input("输出格式 (csv/json, 默认csv): ").strip().lower()
            output_format = format_choice if format_choice in ['csv', 'json'] else 'csv'
            
            try:
                delay = int(input("下载间隔秒数 (默认2): ").strip() or "2")
            except:
                delay = 2
            
            # 批量下载评论
            download_results = downloader.batch_download_comments_by_keyword(
                url_results, limit, sort, language, output_format, delay
            )
            
            # 生成报告
            downloader.generate_report(url_results, download_results)
            
        elif choice == '2':
            # 仅搜索URL
            print("请输入搜索关键词 (多个关键词请用逗号分隔):")
            keywords_input = input().strip()
            if not keywords_input:
                print("❌ 关键词不能为空")
                continue
            
            keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
            
            try:
                max_results = int(input("每个关键词最大视频数 (默认40): ").strip() or "40")
            except:
                max_results = 40
                
            try:
                scroll_times = int(input("页面滚动次数 (默认5): ").strip() or "5")
            except:
                scroll_times = 5
            
            url_results = downloader.batch_search_keywords(keywords, max_results, scroll_times)
            downloader.save_urls_to_files(url_results)
            downloader.generate_report(url_results=url_results)
            
        elif choice == '3':
            # 从文件读取URL并下载评论
            print("请选择URL文件类型:")
            print("1. JSON文件 (包含完整视频信息)")
            print("2. CSV文件")
            print("3. TXT文件 (纯URL列表)")
            
            file_type = input("请选择 (1-3): ").strip()
            filename = input("请输入文件路径: ").strip()
            
            if not filename or not os.path.exists(filename):
                print("❌ 文件不存在")
                continue
            
            try:
                video_list = []
                
                if file_type == '1':
                    # JSON文件
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if '详细数据' in data:
                            for videos in data['详细数据'].values():
                                video_list.extend(videos)
                        else:
                            video_list = data
                            
                elif file_type == '2':
                    # CSV文件
                    df = pd.read_csv(filename)
                    video_list = df.to_dict('records')
                    
                elif file_type == '3':
                    # TXT文件
                    with open(filename, 'r', encoding='utf-8') as f:
                        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        for i, url in enumerate(urls):
                            video_id = downloader.extract_video_id(url)
                            video_list.append({
                                "序号": i + 1,
                                "标题": f"Video_{video_id}",
                                "URL": url,
                                "视频ID": video_id,
                                "类型": "watch",
                                "关键词": "从文件导入",
                                "获取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                
                if not video_list:
                    print("❌ 文件中没有找到有效的视频信息")
                    continue
                
                print(f"✅ 从文件中读取到 {len(video_list)} 个视频")
                
                # 评论下载参数
                try:
                    limit = int(input("每个视频评论数量限制 (默认1000): ").strip() or "1000")
                except:
                    limit = 1000
                
                sort_choice = input("排序方式 (0=热门, 1=最新, 默认1): ").strip() or "1"
                sort = int(sort_choice) if sort_choice in ['0', '1'] else 1
                
                language = input("语言设置 (如: zh, en, 默认自动): ").strip() or None
                
                format_choice = input("输出格式 (csv/json, 默认csv): ").strip().lower()
                output_format = format_choice if format_choice in ['csv', 'json'] else 'csv'
                
                try:
                    delay = int(input("下载间隔秒数 (默认2): ").strip() or "2")
                except:
                    delay = 2
                
                # 将视频列表转换为关键词格式以兼容新方法
                keyword_results = {"从文件导入": video_list}
                
                # 批量下载评论
                download_results = downloader.batch_download_comments_by_keyword(
                    keyword_results, limit, sort, language, output_format, delay
                )
                
                downloader.generate_report(download_results=download_results)
                
            except Exception as e:
                print(f"❌ 处理文件时出错: {e}")
                
        elif choice == '4':
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重试")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序出现错误: {e}") 