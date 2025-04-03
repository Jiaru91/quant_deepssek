from typing import List, Dict, Any, Optional, AsyncGenerator
from openai import OpenAI
from config.dev import settings
import pandas as pd
import numpy as np
from datetime import datetime
import os
from sklearn.preprocessing import MinMaxScaler
from textblob import TextBlob
import re
import json


class FinancialAnalyzer:
    """金融分析服务"""

    def __init__(self):
        """初始化服务"""
        # 使用 DeepSeek 配置
        print("=== Configuration Debug ===")
        print(f"Using DeepSeek API base: {settings.deepseek_api_base}")
        print(f"Using DeepSeek model: {settings.deepseek_model}")
        print("=========================")

        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base
        )
        self.model = settings.deepseek_model
        self.scaler = MinMaxScaler()

    async def analyze_news(self, news_items: List[Dict[str, Any]], symbol: str) -> AsyncGenerator[str, None]:
        """分析新闻内容并提取关键信息"""
        # 格式化新闻内容
        news_text = self._format_news_for_prompt(news_items)

        # 构建 prompt
        prompt = f"""
        请分析以下关于 {symbol} 的新闻，提供详细分析报告。重点关注：
        1. 长期发展战略和规划
        2. 市场竞争力和行业地位
        3. 技术创新和研发进展
        4. 财务状况和业绩表现
        5. 风险因素和挑战

        新闻内容：
        {news_text}

        请提供：
        1. 关键事件时间线
        2. 主要影响因素分析
        3. 长期发展前景评估
        4. 风险提示
        5. 综合建议
        """

        try:
            # 发送初始状态
            yield json.dumps({
                "type": "status",
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })

            # 流式获取分析结果
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                stream=True
            )

            analysis = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    analysis += chunk.choices[0].delta.content
                    yield json.dumps({
                        "type": "content",
                        "content": chunk.choices[0].delta.content
                    })

            # 分析新闻情感
            sentiment_analysis = self._analyze_sentiment_consistency(news_items)

            # 发送最终结果
            yield json.dumps({
                "type": "complete",
                "data": {
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat(),
                    "source_count": len(news_items),
                    "symbol": symbol,
                    "sentiment_consistency": sentiment_analysis
                }
            })

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "error": str(e)
            })

    async def analyze_financial_report(self, report_text: str, report_type: str, symbol: str) -> AsyncGenerator[
        str, None]:
        """分析财务报告并提取关键数据"""
        prompt = f"""
        请分析以下 {symbol} 的{report_type}，提取关键财务指标并进行分析。重点关注：
        1. 收入和利润增长
        2. 毛利率和净利率变化
        3. 现金流状况
        4. 资产负债结构
        5. 研发投入
        6. 主要业务板块表现

        报告内容：
        {report_text}

        请提供：
        1. 核心财务指标及同比变化
        2. 业务结构分析
        3. 财务健康度评估
        4. 增长动力分析
        5. 风险点识别
        6. 未来展望
        """

        try:
            # 发送初始状态
            yield json.dumps({
                "type": "status",
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })

            # 流式获取分析结果
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                stream=True
            )

            analysis = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    analysis += chunk.choices[0].delta.content
                    yield json.dumps({
                        "type": "content",
                        "content": chunk.choices[0].delta.content
                    })

            # 提取关键指标
            metrics = self._extract_financial_metrics(analysis)

            # 发送最终结果
            yield json.dumps({
                "type": "complete",
                "data": {
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat(),
                    "report_type": report_type,
                    "symbol": symbol,
                    "key_metrics": metrics
                }
            })

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "error": str(e)
            })

    async def generate_prediction(
            self,
            news_analysis: Dict[str, Any],
            financial_analysis: Dict[str, Any],
            technical_data: pd.DataFrame,
            symbol: str
    ) -> AsyncGenerator[str, None]:
        """生成综合预测"""
        # 计算技术指标
        technical_indicators = self.analyze_technical_indicators(technical_data)

        # 构建 prompt
        prompt = f"""
        请基于以下信息，对 {symbol} 进行综合分析并给出预测：

        1. 新闻分析：
        {news_analysis.get('analysis', '无新闻分析')}

        2. 财报分析：
        {financial_analysis.get('analysis', '无财报分析')}

        3. 技术指标：
        - 趋势：{technical_indicators['trend']}
        - MA5：{technical_indicators['ma5']}
        - MA10：{technical_indicators['ma10']}
        - RSI：{technical_indicators['rsi']}

        请提供：
        1. 短期趋势（1-7天）
        2. 中期趋势（1-3个月）
        3. 长期趋势（3-12个月）
        4. 主要风险因素
        5. 投资建议
        6. 目标价格区间
        """

        try:
            # 发送初始状态
            yield json.dumps({
                "type": "status",
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })

            # 流式获取预测结果
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                stream=True
            )

            prediction = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    prediction += chunk.choices[0].delta.content
                    yield json.dumps({
                        "type": "content",
                        "content": chunk.choices[0].delta.content
                    })

            # 计算置信度
            confidence_score = self._calculate_confidence_score(prediction)

            # 发送最终结果
            yield json.dumps({
                "type": "complete",
                "data": {
                    "prediction": prediction,
                    "timestamp": datetime.now().isoformat(),
                    "symbol": symbol,
                    "confidence_score": confidence_score
                }
            })

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "error": str(e)
            })

    def analyze_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """
        计算技术指标

        参数:
        - data: 股票价格数据

        返回:
        - 技术指标分析结果
        """
        if data.empty:
            return {
                "ma5": None,
                "ma10": None,
                "rsi": None,
                "trend": "unknown"
            }

        # 计算移动平均线
        data['MA5'] = data['close_price'].rolling(window=5).mean()
        data['MA10'] = data['close_price'].rolling(window=10).mean()

        # 计算RSI
        delta = data['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        # 获取最新值
        latest = data.iloc[-1]
        ma5 = latest['MA5']
        ma10 = latest['MA10']
        rsi = latest['RSI']

        # 判断趋势
        if ma5 > ma10:
            trend = "上升"
        elif ma5 < ma10:
            trend = "下降"
        else:
            trend = "横盘"

        return {
            "ma5": round(ma5, 2) if not pd.isna(ma5) else None,
            "ma10": round(ma10, 2) if not pd.isna(ma10) else None,
            "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
            "trend": trend
        }

    def _format_news_for_prompt(self, news_items: List[Dict[str, Any]]) -> str:
        """格式化新闻内容用于 prompt"""
        formatted_news = []
        for item in news_items:
            formatted_news.append(
                f"标题：{item['title']}\n时间：{item['time']}\n来源：{item['source']}\n内容：{item['content']}\n")
        return "\n".join(formatted_news)

    def _format_technical_data(self, data: pd.DataFrame) -> str:
        """格式化技术指标数据"""
        if data.empty:
            return "无技术数据"

        latest_data = data.iloc[-1]
        return f"""
        最新技术指标：
        - 收盘价：{latest_data.get('close', 'N/A')}
        - 成交量：{latest_data.get('volume', 'N/A')}
        - 最高价：{latest_data.get('high', 'N/A')}
        - 最低价：{latest_data.get('low', 'N/A')}
        """

    def _analyze_sentiment_consistency(self, news_items: List[Dict[str, Any]]) -> float:
        """分析新闻情感一致性"""
        sentiments = []
        for item in news_items:
            blob = TextBlob(item["content"])
            sentiment = blob.sentiment.polarity
            sentiments.append(sentiment)

        if not sentiments:
            return 0.0

        sentiment_std = np.std(sentiments)
        return 1 - min(sentiment_std, 1)  # 标准差越小，一致性越高

    def _extract_financial_metrics(self, analysis: str) -> Dict[str, Any]:
        """从分析文本中提取关键财务指标"""
        metrics = {}

        # 提取营收
        revenue_match = re.search(r"营业收入[：:]\s*([\d,.]+)", analysis)
        if revenue_match:
            metrics["revenue"] = float(revenue_match.group(1).replace(",", ""))

        # 提取净利润
        profit_match = re.search(r"净利润[：:]\s*([\d,.]+)", analysis)
        if profit_match:
            metrics["net_profit"] = float(profit_match.group(1).replace(",", ""))

        return metrics

    def _calculate_confidence_score(self, prediction: str) -> float:
        """计算预测的置信度分数"""
        # 基于预测文本的特征计算置信度
        confidence_factors = []

        # 1. 预测的详细程度
        if len(prediction.split("\n")) > 5:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.4)

        # 2. 是否包含具体数据
        if re.search(r"\d+\.?\d*", prediction):
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)

        # 3. 是否包含风险提示
        if "风险" in prediction or "挑战" in prediction:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)

        return round(np.mean(confidence_factors), 2) 