#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量YouTube视频URL获取工具
基于关键词搜索批量获取视频URL和基本信息
"""

import os
import time
import json
import csv
import requests
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


class BatchURLCrawler:
    def __init__(self, output_dir="video_urls", headless=True, timeout=30):
        """
        初始化批量URL爬虫
        
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
            
        print(f"🚀 批量URL爬虫初始化完成")
        print(f"📁 输出目录: {output_dir}")
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

    def get_urls_from_keyword(self, keyword, max_results=20, scroll_times=5):
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

    def batch_search_keywords(self, keywords, max_results_per_keyword=20, scroll_times=5):
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

    def save_to_csv(self, results, filename=None):
        """保存结果到CSV文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_urls_{timestamp}.csv"
            
        filepath = os.path.join(self.output_dir, filename)
        
        # 合并所有结果
        all_videos = []
        for keyword, videos in results.items():
            all_videos.extend(videos)
            
        if all_videos:
            df = pd.DataFrame(all_videos)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"💾 CSV文件已保存: {filepath}")
            print(f"📊 共保存 {len(all_videos)} 条记录")
        else:
            print("⚠️ 没有数据可保存")

    def save_to_json(self, results, filename=None):
        """保存结果到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_urls_{timestamp}.json"
            
        filepath = os.path.join(self.output_dir, filename)
        
        # 添加统计信息
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
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"💾 JSON文件已保存: {filepath}")

    def save_urls_only(self, results, filename=None):
        """仅保存URL列表到文本文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"urls_only_{timestamp}.txt"
            
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for keyword, videos in results.items():
                f.write(f"# 关键词: {keyword}\n")
                for video in videos:
                    f.write(f"{video['URL']}\n")
                f.write("\n")
                
        print(f"💾 URL列表已保存: {filepath}")

    def generate_report(self, results):
        """生成搜索报告"""
        print(f"\n{'='*60}")
        print("📊 搜索结果统计报告")
        print(f"{'='*60}")
        
        total_videos = 0
        for keyword, videos in results.items():
            video_count = len(videos)
            total_videos += video_count
            
            # 统计视频类型
            watch_count = sum(1 for v in videos if v['类型'] == 'watch')
            shorts_count = sum(1 for v in videos if v['类型'] == 'shorts')
            
            print(f"🔍 关键词: {keyword}")
            print(f"   📺 总视频数: {video_count}")
            print(f"   🎬 普通视频: {watch_count}")
            print(f"   📱 Shorts: {shorts_count}")
            print()
            
        print(f"🎯 总计: {len(results)} 个关键词，{total_videos} 个视频")
        print(f"{'='*60}")


def main():
    """主函数示例"""
    print("🎬 YouTube批量URL获取工具")
    print("=" * 50)
    
    # 初始化爬虫
    crawler = BatchURLCrawler(
        output_dir="video_urls_output",
        headless=True,  # 设置为False可以看到浏览器操作
        timeout=30
    )
    
    while True:
        print(f"\n{'='*50}")
        print("请选择操作模式:")
        print("1. 单个关键词搜索")
        print("2. 批量关键词搜索")
        print("3. 从文件读取关键词批量搜索")
        print("4. 退出")
        print("=" * 50)
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == '1':
            # 单个关键词搜索
            keyword = input("请输入搜索关键词: ").strip()
            if not keyword:
                print("❌ 关键词不能为空")
                continue
                
            try:
                max_results = int(input("最大视频数量 (默认20): ").strip() or "20")
            except:
                max_results = 20
                
            try:
                scroll_times = int(input("页面滚动次数 (默认5): ").strip() or "5")
            except:
                scroll_times = 5
            
            results = {keyword: crawler.get_urls_from_keyword(keyword, max_results, scroll_times)}
            
            # 保存结果
            save_format = input("保存格式 (csv/json/txt/all，默认csv): ").strip() or "csv"
            
            if save_format in ['csv', 'all']:
                crawler.save_to_csv(results)
            if save_format in ['json', 'all']:
                crawler.save_to_json(results)
            if save_format in ['txt', 'all']:
                crawler.save_urls_only(results)
                
            crawler.generate_report(results)
            
        elif choice == '2':
            # 批量关键词搜索
            print("请输入关键词，每行一个，输入空行结束:")
            keywords = []
            while True:
                keyword = input().strip()
                if not keyword:
                    break
                keywords.append(keyword)
                
            if not keywords:
                print("❌ 至少需要一个关键词")
                continue
                
            try:
                max_results = int(input("每个关键词最大视频数 (默认20): ").strip() or "20")
            except:
                max_results = 20
                
            try:
                scroll_times = int(input("页面滚动次数 (默认5): ").strip() or "5")
            except:
                scroll_times = 5
            
            results = crawler.batch_search_keywords(keywords, max_results, scroll_times)
            
            # 保存结果
            save_format = input("保存格式 (csv/json/txt/all，默认all): ").strip() or "all"
            
            if save_format in ['csv', 'all']:
                crawler.save_to_csv(results)
            if save_format in ['json', 'all']:
                crawler.save_to_json(results)
            if save_format in ['txt', 'all']:
                crawler.save_urls_only(results)
                
            crawler.generate_report(results)
            
        elif choice == '3':
            # 从文件读取关键词
            filename = input("请输入关键词文件路径 (默认keywords.txt): ").strip() or "keywords.txt"
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    keywords = [line.strip() for line in f if line.strip()]
                    
                if not keywords:
                    print("❌ 文件中没有找到关键词")
                    continue
                    
                print(f"✅ 从文件中读取到 {len(keywords)} 个关键词")
                
                try:
                    max_results = int(input("每个关键词最大视频数 (默认20): ").strip() or "20")
                except:
                    max_results = 20
                    
                try:
                    scroll_times = int(input("页面滚动次数 (默认5): ").strip() or "5")
                except:
                    scroll_times = 5
                
                results = crawler.batch_search_keywords(keywords, max_results, scroll_times)
                
                # 自动保存所有格式
                crawler.save_to_csv(results)
                crawler.save_to_json(results)
                crawler.save_urls_only(results)
                crawler.generate_report(results)
                
            except FileNotFoundError:
                print(f"❌ 文件 '{filename}' 不存在")
            except Exception as e:
                print(f"❌ 读取文件时出错: {e}")
                
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