#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量YouTube评论下载工具演示脚本
快速测试功能
"""

from batch_comment_downloader import BatchCommentDownloader
import os

def demo_test():
    """演示测试函数"""
    print("🎬 批量YouTube评论下载工具 - 演示模式")
    print("=" * 60)
    
    # 初始化下载器
    downloader = BatchCommentDownloader(
        output_dir="demo_output",
        headless=True,
        timeout=30
    )
    
    # 演示关键词搜索
    print("\n🔍 演示: 搜索关键词获取视频URL")
    test_keywords = ["ChatGPT"]  # 使用一个简单的关键词测试
    
    try:
        # 搜索视频URL (少量测试)
        url_results = downloader.batch_search_keywords(
            keywords=test_keywords,
            max_results_per_keyword=3,  # 只获取3个视频进行测试
            scroll_times=2  # 减少滚动次数
        )
        
        if not any(url_results.values()):
            print("❌ 没有找到任何视频")
            return
        
        # 保存URL结果
        downloader.save_urls_to_files(url_results)
        
        # 合并所有视频
        all_videos = []
        for videos in url_results.values():
            all_videos.extend(videos)
        
        print(f"\n⬇️ 演示: 下载 {len(all_videos)} 个视频的评论")
        
        # 批量下载评论 (少量测试)
        download_results = downloader.batch_download_comments(
            video_list=all_videos,
            limit=20,  # 每个视频只下载20条评论
            sort=1,    # 最新评论
            language=None,
            pretty=True,
            delay=1    # 1秒延迟
        )
        
        # 生成报告
        downloader.generate_report(url_results, download_results)
        
        print(f"\n🎉 演示完成! 输出目录: demo_output/")
        print("📁 你可以查看以下文件:")
        print("   - demo_output/urls/ (视频URL文件)")
        print("   - demo_output/comments/ (评论JSON文件)")
        print("   - demo_output/logs/ (下载日志)")
        
    except Exception as e:
        print(f"❌ 演示过程中出错: {e}")

if __name__ == "__main__":
    demo_test() 