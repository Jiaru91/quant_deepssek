from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config.dev import settings


class DataCleaner:
    """数据清洗和噪音处理服务"""

    def __init__(self):
        self.noise_threshold = getattr(settings, "max_noise_threshold", 0.3)


    def clean_news_data(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清洗新闻数据，去除噪音

        Args:
            news_items: 原始新闻数据列表

        Returns:
            List[Dict]: 清洗后的新闻数据列表
        """
        cleaned_news = []

        for item in news_items:
            # 1. 检查必要字段是否存在
            if not all(key in item for key in ['title', 'content', 'time']):
                continue

            # 2. 检查内容长度
            if len(item['content']) < 50:  # 内容过短可能是无效信息
                continue

            # 3. 检查时间有效性
            try:
                news_time = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                if news_time > datetime.now() + timedelta(days=1):  # 未来日期无效
                    continue
            except (ValueError, TypeError):
                continue

            # 4. 去除广告和推广内容
            if self._is_advertisement(item['title'], item['content']):
                continue

            # 5. 检查内容相关性
            if not self._is_relevant_content(item['content']):
                continue

            cleaned_news.append(item)

        return cleaned_news

    def clean_financial_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """清洗财务数据，处理异常值和缺失值

        Args:
            data: 原始财务数据

        Returns:
            pd.DataFrame: 清洗后的财务数据
        """
        # 1. 处理缺失值
        data = self._handle_missing_values(data)

        # 2. 处理异常值
        data = self._handle_outliers(data)

        # 3. 数据标准化
        data = self._normalize_data(data)

        return data

    def _is_advertisement(self, title: str, content: str) -> bool:
        """检查是否为广告内容"""
        ad_indicators = [
            "推广", "广告", "sponsored", "promoted",
            "立即购买", "点击购买", "优惠", "折扣",
            "限时", "特价", "活动"
        ]

        text = (title + " " + content).lower()
        return any(indicator in text for indicator in ad_indicators)

    def _is_relevant_content(self, content: str) -> bool:
        """检查内容相关性"""
        irrelevant_indicators = [
            "游戏", "娱乐", "明星", "八卦",
            "点击量", "转发量", "观看量"
        ]

        content = content.lower()
        irrelevant_count = sum(1 for indicator in irrelevant_indicators if indicator in content)
        return irrelevant_count <= 2  # 允许少量不相关词

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        # 1. 对于时间序列数据，使用前向填充
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = data[numeric_cols].fillna(method='ffill')

        # 2. 对于仍然存在的缺失值，使用中位数填充
        data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())

        # 3. 对于分类数据，使用众数填充
        categorical_cols = data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            data[col] = data[col].fillna(data[col].mode()[0])

        return data

    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理异常值"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            # 使用 IQR 方法检测异常值
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # 将异常值替换为边界值
            data[col] = data[col].clip(lower=lower_bound, upper=upper_bound)

        return data

    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据标准化"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            mean = data[col].mean()
            std = data[col].std()
            if std != 0:
                data[col] = (data[col] - mean) / std

        return data