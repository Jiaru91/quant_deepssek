import streamlit as st
import httpx
import pandas as pd
import json
import time

API_BASE = "http://web:8000/api/v1/stock"

st.set_page_config(page_title="AI量化分析系统", layout="centered")
st.title("📈 AI量化分析系统")

symbol = st.text_input("请输入股票代码（如 AAPL）", "AAPL")

# 查询历史数据
if st.button("查询历史数据"):
    with st.spinner("正在获取历史数据..."):
        try:
            resp = httpx.get(f"{API_BASE}/stock/{symbol}", timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index("date").sort_index()
                st.line_chart(df["close_price"])
                st.success("✅ 数据展示成功")
            else:
                st.error("❌ 获取数据失败")
        except Exception as e:
            st.error(f"❌ 请求异常: {e}")

# 分析和预测
if st.button("分析和预测"):
    st.subheader("📊 AI分析结果")

    with st.spinner("AI正在分析中..."):
        try:
            with httpx.stream("GET", f"{API_BASE}/stock/{symbol}/analyze", timeout=None) as stream:
                full_text = ""
                last_render_time = time.time()
                placeholder = st.empty()
                decoder = json.JSONDecoder()
                buffer = ""

                for line in stream.iter_lines():
                    if not line:
                        continue

                    if isinstance(line, bytes):
                        line = line.decode("utf-8")

                    buffer += line

                    try:
                        while buffer:
                            obj, index = decoder.raw_decode(buffer)
                            buffer = buffer[index:].lstrip()
                            json_data = obj

                            if json_data["type"] == "content":
                                content = json_data["content"]
                                full_text += content
                                if time.time() - last_render_time > 0.2:
                                    placeholder.markdown(full_text)
                                    last_render_time = time.time()

                            elif json_data["type"] == "complete":
                                if "confidence_score" in json_data.get("data", {}):

                                    score = json_data["data"]["confidence_score"]

                                    st.markdown(f"📌 **置信度评分**: `{float(score):.2f}`")

                                else:

                                    st.info("✅ 当前阶段分析完成")  # ✅ 不再报错，正常提示分析完成

                            elif json_data["type"] == "error":
                                st.error("❌ 分析出错：" + json_data["error"])
                                break

                    except json.JSONDecodeError as e:
                        # 如果 JSON 不完整，继续读取下一段
                        continue

        except Exception as e:
            st.error(f"❌ 请求失败: {e}")
