"""AI service for generating task descriptions."""
import os
from typing import Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    GENAI_AVAILABLE = False
    genai = None  # type: ignore[assignment]
    print(
        "Warning: google-generativeai package not available. "
        "Using fallback description generation."
    )

_configured_api_key: Optional[str] = None


def generate_description(title: str) -> str:
    """
    Generate a task description based on the title using Google Gemini API.

    Args:
        title: The task title

    Returns:
        Generated description string

    Raises:
        ValueError: If GEMINI_API_KEY is not set
        Exception: If API call fails
    """
    # Fallback to simple generation if genai package is not available
    if not GENAI_AVAILABLE:
        return generate_simple_description(title)

    api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:
        # Fallback to simple rule-based generation if API key is not set
        return generate_simple_description(title)

    try:
        description = _generate_with_gemini(title, api_key)
        if description:
            return description
    except Exception as e:  # pragma: no cover - network path
        print(f"Gemini API error: {type(e).__name__}: {str(e)}")

    # Fallback to simple generation on error
    return generate_simple_description(title)


def _generate_with_gemini(title: str, api_key: str) -> Optional[str]:
    """Generate description using Gemini API."""
    global _configured_api_key

    if not GENAI_AVAILABLE:
        return None

    if _configured_api_key != api_key:
        genai.configure(api_key=api_key)
        _configured_api_key = api_key

    prompt = (
        f"タイトル「{title}」にちなんだ説明文を40文字程度で返却してください。\n"
        "説明文のみを出力し、余計な前置きや説明は不要です。"
    )

    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(
        prompt,
        generation_config={
            'temperature': 0.7,
            'max_output_tokens': 100,
        },
    )

    description = getattr(response, "text", "") or ""
    description = description.strip()
    return description or None


def generate_simple_description(title: str) -> str:
    """
    Generate a simple description when Gemini API is not available.
    Uses basic rules to create contextual descriptions.

    Args:
        title: The task title

    Returns:
        Generated description string
    """
    # Analyze title to generate contextual description
    title_lower = title.lower()

    # Action-based generation
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

    # Default simple description
    return f"{title}を実施"
