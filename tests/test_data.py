import asyncio
from app.services.analysis.data_cleaner import DataCleaner
from app.services.analysis.financial_analysis import FinancialAnalyzer
from app.core.database import SessionLocal
from app.models.crawler import News, StockData, FinancialReport
import pandas as pd

from datetime import datetime

def run_quant_analysis(symbol: str = "AAPL"):
    print(f"\n📊 开始量化分析：{symbol}")
    db = SessionLocal()
    cleaner = DataCleaner()
    analyzer = FinancialAnalyzer()

    try:
        # 1. 新闻数据清洗
        news_items = db.query(News).filter(News.symbol == symbol).all()
        news_list = [{
            "title": n.title,
            "content": n.content,
            "source": n.source,
            "time": n.published_date.isoformat()
        } for n in news_items]

        cleaned_news = cleaner.clean_news_data(news_list)
        print(f"📰 原始新闻：{len(news_list)}，清洗后：{len(cleaned_news)}")

        # 2. 股票数据清洗
        stock_records = db.query(StockData).filter(StockData.symbol == symbol).all()
        stock_df = cleaner.clean_financial_data(
            pd.DataFrame([{
                "id": s.id,
                "symbol": s.symbol,
                "date": s.date,
                "open_price": s.open_price,
                "high_price": s.high_price,
                "low_price": s.low_price,
                "close_price": s.close_price,
                "volume": s.volume,
                "created_at": s.created_at
            } for s in stock_records])
        )

        # 3. 异步运行分析
        async def run_async_analysis():
            print("\n🧠 正在进行新闻分析...")
            async for msg in analyzer.analyze_news(cleaned_news, symbol):
                parsed = eval(msg)
                if parsed["type"] == "content":
                    print(parsed["content"], end='', flush=True)
                elif parsed["type"] == "complete":
                    news_analysis = parsed["data"]
                    print("\n✅ 新闻分析完成")
                    break

            print("\n📄 正在进行财报分析...")
            report = db.query(FinancialReport).filter(FinancialReport.symbol == symbol).first()
            if report:
                async for msg in analyzer.analyze_financial_report(report.content, report.report_type, symbol):
                    parsed = eval(msg)
                    if parsed["type"] == "content":
                        print(parsed["content"], end='', flush=True)
                    elif parsed["type"] == "complete":
                        financial_analysis = parsed["data"]
                        print("\n✅ 财报分析完成")
                        break
            else:
                financial_analysis = {"analysis": "无财报"}

            print("\n📈 正在进行预测生成...")
            async for msg in analyzer.generate_prediction(news_analysis={"analysis": "基于新闻的分析..."},
                financial_analysis={"analysis": "基于财务报告的分析..."},
                technical_data=stock_df,
                symbol=symbol
             ):
                parsed = eval(msg)
                if parsed["type"] == "content":
                    print(parsed["content"], end='', flush=True)
                elif parsed["type"] == "complete":
                    print("\n✅ 预测完成！结果：")
                    print(parsed["data"])
                    break

        asyncio.run(run_async_analysis())

    finally:
        db.close()

if __name__ == "__main__":
    run_quant_analysis(symbol="AAPL")