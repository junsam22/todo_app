"""AI service for generating task descriptions."""
import os
import requests
from typing import Optional


def generate_description(title: str) -> str:
    """
    Generate a task description based on the title using Google Gemini API.
    Falls back to simple rule-based generation if API is unavailable.

    Args:
        title: The task title

    Returns:
        Generated description string
    """
    api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:
        return generate_simple_description(title)

    try:
        description = _call_gemini_api(title, api_key)
        if description:
            return description
    except Exception as e:
        print(f"Gemini API error: {e}")

    return generate_simple_description(title)


def _call_gemini_api(title: str, api_key: str) -> Optional[str]:
    """Call Gemini API via REST endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"

    prompt = f"タイトル「{title}」にちなんだ説明文を40文字程度で返却してください。説明文のみを出力し、余計な前置きや説明は不要です。"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 100
        }
    }

    response = requests.post(url, json=payload, timeout=10)

    if response.status_code != 200:
        print(f"Gemini API returned status {response.status_code}: {response.text[:200]}")
        return None

    data = response.json()

    # Extract text from response
    # Response structure: data['candidates'][0]['content']['parts'][0]['text']
    try:
        text = data['candidates'][0]['content']['parts'][0]['text']
        return text.strip() or None
    except (KeyError, IndexError, TypeError) as e:
        print(f"Failed to parse Gemini response: {e}")
        print(f"Response data: {data}")
        return None


def generate_simple_description(title: str) -> str:
    """
    Generate a simple description when Gemini API is not available.
    Uses basic rules to create contextual descriptions.

    Args:
        title: The task title

    Returns:
        Generated description string
    """
    title_lower = title.lower()

    if any(word in title_lower for word in ['作成', '書く', '書き', '執筆']):
        return f"{title}を完了する"
    elif any(word in title_lower for word in ['確認', 'チェック', '検証', 'テスト']):
        return f"{title}を実施"
    elif any(word in title_lower for word in ['修正', '直す', 'fix', 'バグ']):
        return f"{title}対応"
    elif any(word in title_lower for word in ['会議', 'ミーティング', 'mtg', '打ち合わせ']):
        return f"{title}に参加"
    elif any(word in title_lower for word in ['実装', '開発', 'develop', '実装する']):
        return f"{title}を進める"
    elif any(word in title_lower for word in ['調査', '調べる', '研究', 'リサーチ']):
        return f"{title}を行う"

    return f"{title}を実施"
