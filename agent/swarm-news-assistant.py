import streamlit as st
from duckduckgo_search import DDGS
from datetime import datetime
from dotenv import load_dotenv
import openai
import os

# 加载环境变量
load_dotenv()

# 配置OpenAI客户端指向本地模型服务
openai.api_key = "fake-key"  # 本地模型可能不需要实际的key
openai.api_base = "http://localhost:8000/v1"  # 本地模型服务地址

# 初始化页面配置
st.set_page_config(page_title="AI News Processor", page_icon="📰")
st.title("📰 News Inshorts Agent")


def get_completion(prompt, system="", temperature=0.7):
    """调用模型，兼容OpenAI接口"""
    try:
        response = openai.ChatCompletion.create(
            model="local-model",  # 本地模型名称
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"模型调用错误: {str(e)}")
        return None


def search_news(topic):
    """使用DuckDuckGo搜索新闻"""
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=3)
        if results:
            news_results = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['href']}\nSummary: {result['body']}"
                for result in results
            ])
            return news_results
        return f"No news found for {topic}."


def process_news(topic):
    """新闻处理工作流"""
    with st.status("Processing news...", expanded=True) as status:
        # 搜索新闻
        status.write("🔍 Searching for news...")
        raw_news = search_news(topic)

        # 综合分析
        status.write("🔄 Synthesizing information...")
        synthesis_system = """You are a news synthesis expert. Your task is to analyze news articles 
        and create a comprehensive synthesis focusing on key themes, important information, and 
        maintaining journalistic objectivity."""

        synthesis_prompt = f"""Please analyze and synthesize these news articles:
        {raw_news}

        Create a comprehensive synthesis that:
        1. Identifies key themes and important information
        2. Combines information from multiple sources
        3. Maintains factual accuracy and objectivity
        4. Provides context and significance

        Format: 2-3 paragraphs of clear, professional writing."""

        synthesized_news = get_completion(
            prompt=synthesis_prompt,
            system=synthesis_system,
            temperature=0.7
        )

        # 生成总结
        status.write("📝 Creating summary...")
        summary_system = """You are an expert news summarizer combining AP and Reuters style clarity 
        with digital-age brevity. Focus on delivering key information in a concise, engaging format."""

        summary_prompt = f"""Create a professional summary of this news synthesis:
        {synthesized_news}

        Requirements:
        1. Single paragraph (250-400 words)
        2. Lead with the most important development
        3. Include key stakeholders and their actions
        4. Explain significance and implications
        5. Use clear, active voice
        6. Maintain journalistic objectivity

        Start directly with the news content without any introductory phrases."""

        final_summary = get_completion(
            prompt=summary_prompt,
            system=summary_system,
            temperature=0.5
        )

        return raw_news, synthesized_news, final_summary


# 用户界面
with st.container():
    topic = st.text_input("输入新闻主题:", value="artificial intelligence")
    col1, col2 = st.columns([1, 4])
    with col1:
        process_button = st.button("处理新闻", type="primary")
    with col2:
        model_endpoint = st.text_input("模型服务地址:",
                                       value="http://localhost:8000/v1",
                                       help="本地模型API地址")

if process_button:
    if topic:
        # 更新API地址
        openai.api_base = model_endpoint

        try:
            raw_news, synthesized_news, final_summary = process_news(topic)

            # 显示结果
            st.header(f"📝 新闻总结: {topic}")
            st.markdown(final_summary)

            # 详细信息展开选项
            with st.expander("查看原始新闻"):
                st.text(raw_news)
            with st.expander("查看综合分析"):
                st.markdown(synthesized_news)

        except Exception as e:
            st.error(f"处理过程中出现错误: {str(e)}")
    else:
        st.error("请输入新闻主题！")