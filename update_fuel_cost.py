#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广东省燃料成本分析系统 - 每日数据更新脚本
"""

import requests
import re
import os
from datetime import datetime

class FuelCostUpdater:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.data_dir = os.path.expanduser('~/Desktop/燃料成本')
        self.html_file = os.path.join(self.data_dir, 'guangdong_fuel_cost_system.html')
        
    def get_cctd_prices(self):
        """从CCTD获取煤炭价格"""
        print("正在获取CCTD煤炭价格...")
        try:
            url = 'https://www.cctd.com.cn'
            response = requests.get(url, headers=self.headers, timeout=15)
            text = response.content.decode('gbk', errors='ignore')
            
            # 提取价格：HTML格式 >717</em>...元/吨
            price_pattern = r'>(\d{3,4})</em>.*?元/吨'
            matches = re.findall(price_pattern, text)
            
            # 提取日期
            date_pattern = r'日期[：:](\d{2}-\d{2})'
            dates = re.findall(date_pattern, text)
            
            if len(matches) >= 10:
                prices = {
                    '综合交易5500': {'price': int(matches[1]), 'date': dates[0] if dates else '06-01'},
                    '综合交易5000': {'price': int(matches[3]), 'date': dates[1] if len(dates) > 1 else '06-01'},
                    '综合交易4500': {'price': int(matches[5]), 'date': dates[2] if len(dates) > 2 else '06-01'},
                    '年度长协5500': {'price': int(matches[7]), 'date': dates[3] if len(dates) > 3 else '06-01'},
                    '年度长协5000': {'price': int(matches[8]), 'date': dates[4] if len(dates) > 4 else '06-01'},
                    '年度长协4500': {'price': int(matches[9]), 'date': dates[5] if len(dates) > 5 else '06-01'},
                }
                print(f"CCTD价格获取成功:")
                for k, v in prices.items():
                    print(f"  {k}: {v['price']}元/吨 ({v['date']})")
                return prices
                    
        except Exception as e:
            print(f"获取CCTD价格失败: {e}")
        
        return None
    
    def get_shpgx_lng_prices(self):
        """从SHPGX获取LNG价格"""
        print("正在获取SHPGX LNG价格...")
        try:
            url = 'https://www.shpgx.com/html/jgsj/lng/lngbjhq.html'
            response = requests.get(url, headers=self.headers, timeout=15)
            text = response.text
            
            # 提取广东地区LNG价格
            # 珠海接收站 广东(粤东) XXXX元/吨
            pattern = r'珠海接收站.*?广东.*?(\d{4})元/吨'
            zhuhai_matches = re.findall(pattern, text, re.DOTALL)
            
            # 粤东接收站 广东(粤东) XXXX元/吨  
            pattern2 = r'粤东接收站.*?广东.*?(\d{4})元/吨'
            yuedong_matches = re.findall(pattern2, text, re.DOTALL)
            
            lng_prices = {}
            if zhuhai_matches:
                lng_prices['珠海金湾'] = int(zhuhai_matches[0])
            if yuedong_matches:
                lng_prices['粤东揭阳'] = int(yuedong_matches[0])
            
            # 全国LNG出厂价格
            pattern3 = r'中国LNG出厂价格.*?(\d{4})'
            national_match = re.findall(pattern3, text)
            if national_match:
                lng_prices['全国出厂价'] = int(national_match[0])
            
            if lng_prices:
                print(f"SHPGX LNG价格获取成功: {lng_prices}")
                return lng_prices
                    
        except Exception as e:
            print(f"获取SHPGX LNG价格失败: {e}")
        
        return None
    
    def update_html(self, cctd_prices=None, lng_prices=None):
        """更新HTML文件"""
        print("正在更新HTML文件...")
        
        if not os.path.exists(self.html_file):
            print(f"HTML文件不存在: {self.html_file}")
            return False
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新日期
        today = datetime.now().strftime('%Y-%m-%d')
        today_cn = datetime.now().strftime('%Y年%-m月%-d日')
        content = re.sub(r'数据更新时间：\d{4}年\d{1,2}月\d{1,2}日', f'数据更新时间：{today_cn}', content)
        
        # 更新CCTD价格
        if cctd_prices:
            # 获取最新日期
            latest_date = cctd_prices.get('综合交易5500', {}).get('date', '06-01')
            month, day = latest_date.split('-')
            date_str = f"2026-{month}-{day}"
            
            # 更新综合交易价格
            cctd_line = f"综合交易：5500大卡 {cctd_prices['综合交易5500']['price']}元/吨 | 5000大卡 {cctd_prices['综合交易5000']['price']}元/吨 | 4500大卡 {cctd_prices['综合交易4500']['price']}元/吨（{date_str}）"
            content = re.sub(r'综合交易：5500大卡 \d+元/吨 \| 5000大卡 \d+元/吨 \| 4500大卡 \d+元/吨（\d{4}-\d{2}-\d{2}）', cctd_line, content)
            
            # 更新年度长协价格
            nxd_date = cctd_prices.get('年度长协5500', {}).get('date', '06-01')
            nxd_month, nxd_day = nxd_date.split('-')
            nxd_date_str = f"2026-{nxd_month}-{nxd_day}"
            nxd_line = f"年度长协：5500大卡 {cctd_prices['年度长协5500']['price']}元/吨 | 5000大卡 {cctd_prices['年度长协5000']['price']}元/吨 | 4500大卡 {cctd_prices['年度长协4500']['price']}元/吨（{nxd_date_str}）"
            content = re.sub(r'年度长协：5500大卡 \d+元/吨 \| 5000大卡 \d+元/吨 \| 4500大卡 \d+元/吨（\d{4}-\d{2}-\d{2}）', nxd_line, content)
        
        # 保存更新后的文件
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"HTML文件更新完成: {self.html_file}")
        return True
    
    def run(self):
        """执行更新流程"""
        print(f"=== 广东省燃料成本分析系统数据更新 ===")
        print(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 获取数据
        cctd_prices = self.get_cctd_prices()
        lng_prices = self.get_shpgx_lng_prices()
        
        # 更新HTML
        success = self.update_html(cctd_prices, lng_prices)
        
        if success:
            print("\n数据更新完成！")
        else:
            print("\n数据更新失败！")
        
        return success

if __name__ == '__main__':
    updater = FuelCostUpdater()
    updater.run()
