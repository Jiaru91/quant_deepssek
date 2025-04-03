from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.crawler import StockData, News, FinancialReport
from app.models.analysis import AnalysisResult  # 你要确保这个模型已存在
from app.services.analysis.data_cleaner import DataCleaner
from app.services.analysis.financial_analysis import FinancialAnalyzer
from app.crawlers.financial_report import FinancialReportCrawler
from app.crawlers.news import NewsCrawler
from app.crawlers.yahoo_finance import YahooFinanceCrawler

import pandas as pd
from datetime import datetime
import asyncio
import json

router = APIRouter()

@router.get("/stock/{symbol}")
def get_stock_data(symbol: str, db: Session = Depends(get_db)):
    records = db.query(StockData).filter(StockData.symbol == symbol).order_by(StockData.date).all()

    if not records:
        # 调用三个爬虫
        YahooFinanceCrawler(db).crawl_stock_data([symbol], period="1y")
        FinancialReportCrawler(db).crawl_financial_reports(symbol, report_type="10-K")
        NewsCrawler(db).crawl_news([symbol], days=7)

        # 重新查询
        records = db.query(StockData).filter(StockData.symbol == symbol).order_by(StockData.date).all()
        if not records:
            raise HTTPException(status_code=404, detail="No stock data found or failed to fetch.")

    df = pd.DataFrame([{
        "date": r.date,
        "open": r.open_price,
        "high": r.high_price,
        "low": r.low_price,
        "close_price": r.close_price,
        "volume": r.volume
    } for r in records])

    return df.to_dict(orient="records")


@router.get("/stock/{symbol}/analyze")
async def analyze_stock(symbol: str, db: Session = Depends(get_db)):

    cleaner = DataCleaner()
    analyzer = FinancialAnalyzer()

    # 新闻清洗
    raw_news = db.query(News).filter(News.symbol == symbol).all()
    cleaned_news = cleaner.clean_news_data([{
        "title": n.title,
        "content": n.content,
        "time": n.published_date.isoformat() if n.published_date else "",
        "source": n.source or ""
    } for n in raw_news])

    # 财报获取
    latest_report = db.query(FinancialReport).filter(FinancialReport.symbol == symbol).order_by(FinancialReport.report_date.desc()).first()
    report_text = latest_report.content if latest_report else ""
    report_type = latest_report.report_type if latest_report else "季度报告"

    # 股票数据清洗
    raw_stock = db.query(StockData).filter(StockData.symbol == symbol).order_by(StockData.date).all()
    stock_df = pd.DataFrame([{
        "date": r.date,
        "open": r.open_price,
        "high": r.high_price,
        "low": r.low_price,
        "close_price": r.close_price,
        "volume": r.volume
    } for r in raw_stock])
    stock_df = cleaner.clean_financial_data(stock_df)

    # 返回 StreamingResponse
    async def stream_response():
        news_analysis = ""
        financial_analysis = ""
        prediction = ""
        prediction_data = {}

        try:
            # 新闻分析流
            async for chunk in analyzer.analyze_news(cleaned_news, symbol):
                yield chunk + "\n"
                data = json.loads(chunk)
                if data.get("type") == "content":
                    news_analysis += data.get("content", "")
        except Exception as e:
            yield json.dumps({"type": "error", "error": f"新闻分析失败: {str(e)}"})

        try:
            # 财报分析流
            async for chunk in analyzer.analyze_financial_report(report_text, report_type, symbol):
                yield chunk + "\n"
                data = json.loads(chunk)
                if data.get("type") == "content":
                    financial_analysis += data.get("content", "")
        except Exception as e:
            yield json.dumps({"type": "error", "error": f"财报分析失败: {str(e)}"})

        try:
            # 综合预测流
            async for chunk in analyzer.generate_prediction(
                    {"analysis": news_analysis},
                    {"analysis": financial_analysis},
                    stock_df,
                    symbol
            ):
                yield chunk + "\n"
                data = json.loads(chunk)
                if data.get("type") == "content":
                    prediction += data.get("content", "")
                elif data.get("type") == "complete":
                    prediction_data = data.get("data", {})
        except Exception as e:
            yield json.dumps({"type": "error", "error": f"预测失败: {str(e)}"})

        try:
            # 存储到数据库
            result = AnalysisResult(
                symbol=symbol,
                news_analysis=news_analysis,
                financial_analysis=financial_analysis,
                prediction=prediction,
                confidence_score=str(prediction_data.get("confidence_score")),
                created_at=datetime.now()
            )
            db.add(result)
            db.commit()
        except Exception as e:
            yield json.dumps({"type": "error", "error": f"数据库保存失败: {str(e)}"})

        # 最后将完整的分析结果结构打包发给前端
        # 最后 yield 终结信号（必须）
        yield json.dumps({
            "type": "complete",
            "data": {
                "symbol": symbol,
                "prediction": prediction,
                "confidence_score": prediction_data.get("confidence_score", None),
                "timestamp": datetime.now().isoformat()
            }
        }) + "\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
