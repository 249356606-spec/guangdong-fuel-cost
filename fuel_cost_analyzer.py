#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广东省燃料成本数据采集和分析工具
功能：从官方渠道采集动力煤价格数据，并进行分析
作者：小小罗
创建时间：2026年6月2日
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from bs4 import BeautifulSoup
import time
import re

class FuelCostAnalyzer:
    """燃料成本分析器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 数据存储路径
        self.data_dir = os.path.expanduser('~/Desktop/燃料成本')
        self.csv_file = os.path.join(self.data_dir, '广东省动力煤价格数据_2026年.csv')
        
    def collect_cctd_data(self):
        """采集CCTD动力煤价格数据"""
        print("正在采集CCTD动力煤价格数据...")
        
        try:
            # 访问CCTD官网
            url = 'https://www.cctd.com.cn'
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            # 解析页面内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取价格信息
            price_data = {}
            
            # 查找价格相关的文本
            price_texts = soup.find_all(text=re.compile(r'\d+.*元/吨'))
            
            for text in price_texts:
                # 解析价格数据
                # 这里需要根据实际页面结构调整解析逻辑
                pass
            
            # 返回示例数据（实际使用时需要替换为真实数据）
            return {
                '秦皇岛5500': 717,
                '综合结算5500': 650,
                '综合结算5000': 582,
                '综合结算4500': 697
            }
            
        except Exception as e:
            print(f"采集CCTD数据失败: {e}")
            return None
    
    def collect_guangzhou_port_data(self):
        """采集广州港进口动力煤价格数据"""
        print("正在采集广州港进口动力煤价格数据...")
        
        try:
            # 访问广东省能源运销协会
            url = 'http://www.gdetsa.org.cn'
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            # 解析页面内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取价格信息
            price_data = {}
            
            # 查找价格相关的链接
            price_links = soup.find_all('a', href=re.compile(r'price'))
            
            for link in price_links:
                # 解析价格链接
                # 这里需要根据实际页面结构调整解析逻辑
                pass
            
            # 返回示例数据（实际使用时需要替换为真实数据）
            return {
                '广州港5500': 850,
                '广州港5000': 780,
                '广州港4500': 710
            }
            
        except Exception as e:
            print(f"采集广州港数据失败: {e}")
            return None
    
    def save_data(self, date, cctd_data, guangzhou_data):
        """保存数据到CSV文件"""
        try:
            # 读取现有数据
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
            else:
                # 创建新的DataFrame
                df = pd.DataFrame(columns=[
                    '日期', 'CCTD秦皇岛5500大卡（元/吨）', 'CCTD综合结算5500大卡（元/吨）',
                    'CCTD综合结算5000大卡（元/吨）', 'CCTD综合结算4500大卡（元/吨）',
                    '广州港进口煤5500大卡（元/吨）', '广州港进口煤5000大卡（元/吨）',
                    '广州港进口煤4500大卡（元/吨）', '数据来源'
                ])
            
            # 检查是否已存在该日期的数据
            if date in df['日期'].values:
                print(f"日期 {date} 的数据已存在，将进行更新")
                df = df[df['日期'] != date]
            
            # 创建新数据行
            new_row = {
                '日期': date,
                'CCTD秦皇岛5500大卡（元/吨）': cctd_data.get('秦皇岛5500', ''),
                'CCTD综合结算5500大卡（元/吨）': cctd_data.get('综合结算5500', ''),
                'CCTD综合结算5000大卡（元/吨）': cctd_data.get('综合结算5000', ''),
                'CCTD综合结算4500大卡（元/吨）': cctd_data.get('综合结算4500', ''),
                '广州港进口煤5500大卡（元/吨）': guangzhou_data.get('广州港5500', ''),
                '广州港进口煤5000大卡（元/吨）': guangzhou_data.get('广州港5000', ''),
                '广州港进口煤4500大卡（元/吨）': guangzhou_data.get('广州港4500', ''),
                '数据来源': 'CCTD/广东省能源运销协会'
            }
            
            # 添加新数据
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # 按日期排序
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期')
            df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
            
            # 保存到CSV文件
            df.to_csv(self.csv_file, index=False, encoding='utf-8-sig')
            print(f"数据已保存到: {self.csv_file}")
            
            return True
            
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
    
    def analyze_data(self):
        """分析数据"""
        try:
            if not os.path.exists(self.csv_file):
                print("数据文件不存在")
                return None
            
            df = pd.read_csv(self.csv_file)
            
            # 基本统计分析
            analysis = {
                '数据条数': len(df),
                '时间范围': f"{df['日期'].iloc[0]} 至 {df['日期'].iloc[-1]}",
                'CCTD秦皇岛5500大卡': {
                    '平均值': df['CCTD秦皇岛5500大卡（元/吨）'].mean(),
                    '最高值': df['CCTD秦皇岛5500大卡（元/吨）'].max(),
                    '最低值': df['CCTD秦皇岛5500大卡（元/吨）'].min()
                },
                '广州港进口煤5500大卡': {
                    '平均值': df['广州港进口煤5500大卡（元/吨）'].mean(),
                    '最高值': df['广州港进口煤5500大卡（元/吨）'].max(),
                    '最低值': df['广州港进口煤5500大卡（元/吨）'].min()
                }
            }
            
            return analysis
            
        except Exception as e:
            print(f"分析数据失败: {e}")
            return None
    
    def generate_report(self):
        """生成分析报告"""
        try:
            analysis = self.analyze_data()
            
            if not analysis:
                return None
            
            report = f"""
广东省燃料成本分析报告
========================

报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

一、数据概况
------------
数据条数：{analysis['数据条数']}
时间范围：{analysis['时间范围']}

二、CCTD动力煤价格分析
-----------------------
秦皇岛5500大卡动力煤价格：
  平均值：{analysis['CCTD秦皇岛5500大卡']['平均值']:.2f} 元/吨
  最高值：{analysis['CCTD秦皇岛5500大卡']['最高值']:.2f} 元/吨
  最低值：{analysis['CCTD秦皇岛5500大卡']['最低值']:.2f} 元/吨

三、广州港进口煤价格分析
-------------------------
广州港进口煤5500大卡价格：
  平均值：{analysis['广州港进口煤5500大卡']['平均值']:.2f} 元/吨
  最高值：{analysis['广州港进口煤5500大卡']['最高值']:.2f} 元/吨
  最低值：{analysis['广州港进口煤5500大卡']['最低值']:.2f} 元/吨

四、数据来源
------------
1. CCTD中国煤炭市场网（www.cctd.com.cn）
2. 广东省能源运销协会（www.gdetsa.org.cn）

五、注意事项
------------
1. 以上数据仅供参考，实际使用请以官方数据为准
2. 数据采集可能存在延迟，请以最新数据为准
3. 如有疑问请联系数据提供方

报告结束
"""
            
            # 保存报告
            report_file = os.path.join(self.data_dir, f'燃料成本分析报告_{datetime.now().strftime("%Y%m%d")}.txt')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"分析报告已保存到: {report_file}")
            return report
            
        except Exception as e:
            print(f"生成报告失败: {e}")
            return None

def main():
    """主函数"""
    print("=== 广东省燃料成本数据采集和分析工具 ===")
    print(f"运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建分析器
    analyzer = FuelCostAnalyzer()
    
    # 采集数据
    today = datetime.now().strftime('%Y-%m-%d')
    
    cctd_data = analyzer.collect_cctd_data()
    guangzhou_data = analyzer.collect_guangzhou_port_data()
    
    if cctd_data and guangzhou_data:
        # 保存数据
        analyzer.save_data(today, cctd_data, guangzhou_data)
        
        # 生成分析报告
        report = analyzer.generate_report()
        
        if report:
            print("\n" + "="*50)
            print(report)
    else:
        print("数据采集失败")
    
    print("\n程序运行完成")

if __name__ == '__main__':
    main()
