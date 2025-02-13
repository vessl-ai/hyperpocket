from typing import Dict, Optional
from hyperpocket.tool import function_tool
import requests
import logging
import os
import openai

logger = logging.getLogger(__name__)

@function_tool()
def summarize_website(
    url: str,
    max_depth: int = 2,
    max_length: int = 1000,
    language: str = "en",
    **kwargs
) -> Dict:
    """
    Crawl website content and provide a comprehensive summary.
    Args:
        url: Website URL to crawl and summarize
        max_depth: Maximum crawl depth (default: 2)
        max_length: Maximum summary length in words (default: 1000)
        language: Summary language ("en" or "ko", default: "en")
    Returns:
        Summary of website content and metadata
    """
    try:
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("Firecrawl API key not found in environment")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Step 1: Submit crawl job
        crawl_response = requests.post(
            "https://api.firecrawl.dev/v1/crawl",
            headers=headers,
            json={
                "url": url,
                "max_depth": max_depth,
                "exclude_tags": ["script", "style", "nav", "footer", "iframe"],
                "wait_for_result": True  # Wait for result to complete
            }
        )
        crawl_response.raise_for_status()
        result = crawl_response.json()

        if not result.get("success"):
            raise ValueError(f"Crawl failed: {result.get('error')}")

        # Get markdown content and metadata
        markdown_content = result["data"]["markdown"]
        metadata = result["data"].get("metadata", {})

        # Generate summary using OpenAI
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not found in environment")

        system_prompt = {
            "en": """You are a helpful assistant that summarizes website content.
Provide a comprehensive summary focusing on:
1. Main purpose/topic of the website
2. Key sections and their content
3. Important information and details
4. Overall structure and organization""",
            "ko": """웹사이트 내용을 요약하는 도우미입니다.
다음 사항에 중점을 두고 종합적인 요약을 제공하세요:
1. 웹사이트의 주요 목적/주제
2. 주요 섹션과 그 내용
3. 중요한 정보와 세부사항
4. 전반적인 구조와 구성"""
        }[language]

        user_prompt = {
            "en": f"""Summarize this website content in {max_length} words or less:

URL: {url}
Title: {metadata.get('title', 'No title')}
Description: {metadata.get('description', 'No description')}

Content:
{markdown_content}""",
            "ko": f"""다음 웹사이트 내용을 {max_length}단어 이내로 요약하세요:

URL: {url}
제목: {metadata.get('title', '제목 없음')}
설명: {metadata.get('description', '설명 없음')}

내용:
{markdown_content}"""
        }[language]

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=max_length * 2
        )

        summary = response.choices[0].message.content

        return {
            "url": url,
            "title": metadata.get("title"),
            "description": metadata.get("description"),
            "summary": summary,
            "pages_crawled": len(result["data"].get("pages", [])),
            "language": language,
            "message": f"Successfully summarized website content from {url}"
        }

    except Exception as e:
        logger.error(f"Error summarizing website: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to summarize website"
        } 