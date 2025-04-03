import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import requests
from sqlalchemy.orm import Session
from app.crawlers.base import BaseCrawler
from app.models.crawler import News
from config.dev import settings

logger = logging.getLogger(__name__)


class NewsCrawler(BaseCrawler):
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_news(self, symbols: List[str], days: int = 7) -> List[Dict[str, Any]]:
        """
        获取新闻数据
        :param symbols: 股票代码列表
        :param days: 获取最近几天的新闻
        :return: 新闻数据列表
        """
        try:
            # 将股票代码列表转换为逗号分隔的字符串
            tickers = ",".join(symbols)

            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": tickers,
                "apikey": self.api_key,
                "limit": 50  # 限制返回的新闻数量
            }

            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "feed" not in data:
                logger.warning(f"未找到股票 {tickers} 的新闻数据")
                return []

            # 过滤最近几天的新闻
            cutoff_date = datetime.now() - timedelta(days=days)
            news_list = []

            for item in data["feed"]:
                time_published = datetime.strptime(item["time_published"], "%Y%m%dT%H%M%S")
                if time_published >= cutoff_date:
                    # 从 ticker_sentiment 中获取相关的股票代码
                    ticker_sentiments = item.get("ticker_sentiment", [])
                    for ticker_info in ticker_sentiments:
                        ticker = ticker_info.get("ticker")
                        if ticker in symbols:
                            # 为每条新闻添加股票代码
                            news_data = {
                                "symbol": ticker,
                                "title": item.get("title", ""),
                                "content": item.get("summary", ""),
                                "source": item.get("source", ""),
                                "url": item.get("url", ""),
                                "time_published": item.get("time_published", "")
                            }
                            news_list.append(news_data)

            return news_list

        except Exception as e:
            logger.error(f"获取股票新闻数据时出错: {str(e)}")
            return []

    def save_news(self, news_data: Dict[str, Any]) -> bool:
        """
        保存新闻到数据库
        :param news_data: 新闻数据
        :return: 是否保存成功
        """
        try:
            # 生成内容哈希
            content = news_data.get("content", "")
            content_hash = self.generate_hash(content)
            url = news_data.get("url", "")

            # 检查是否已存在相同的新闻
            existing_news = self.db.query(News).filter(
                (News.content_hash == content_hash) | (News.url == url)
            ).first()

            if existing_news:
                # 如果新闻已存在但股票代码不同，则更新股票代码
                if existing_news.symbol != news_data.get("symbol"):
                    existing_news.symbol = news_data.get("symbol")
                    self.db.commit()
                    logger.debug(f"更新新闻股票代码: {url}")
                else:
                    logger.debug(f"新闻已存在: {url}")
                return False

            # 创建新闻对象
            news = News(
                symbol=news_data.get("symbol"),
                title=news_data.get("title", ""),
                content=content,
                source=news_data.get("source", ""),
                url=url,
                content_hash=content_hash,
                published_date=datetime.strptime(news_data["time_published"], "%Y%m%dT%H%M%S")
            )

            # 保存到数据库
            self.db.add(news)
            self.db.commit()
            logger.info(f"成功保存新闻: {news.title} ({news.symbol})")
            return True

        except Exception as e:
            logger.error(f"保存新闻时出错: {str(e)}")
            self.db.rollback()
            return False

    def crawl_news(self, symbols: List[str], days: int = 7) -> bool:
        """
        爬取并保存新闻
        :param symbols: 股票代码列表
        :param days: 获取最近几天的新闻
        :return: 是否成功
        """
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
            elif not isinstance(symbols, list):
                logger.error(f"股票代码格式错误: {symbols}")
                return False

            logger.info(f"开始爬取新闻，股票代码: {symbols}")
            news_list = self.fetch_news(symbols, days)

            if not news_list:
                logger.warning(f"未找到任何新闻")
                return True

            # 按股票代码统计保存的新闻数量
            saved_counts = {}
            for news_data in news_list:
                symbol = news_data.get("symbol")
                if self.save_news(news_data):
                    saved_counts[symbol] = saved_counts.get(symbol, 0) + 1

            # 输出每个股票的新闻保存统计
            for symbol in symbols:
                count = saved_counts.get(symbol, 0)
                logger.info(f"成功保存 {count} 条 {symbol} 的新闻")

            total_saved = sum(saved_counts.values())
            logger.info(f"总共成功保存 {total_saved} 条新闻")
            return True

        except Exception as e:
            logger.error(f"爬取新闻时出错: {str(e)}")
            return False 