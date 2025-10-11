#!/usr/bin/env python3
"""Test script for Gemini API integration."""

import os
from ai_service import generate_description

def test_gemini_api():
    """Test Gemini API functionality."""
    print("=== Gemini API Test ===")
    
    # Check if API key is set
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY is not set")
        print("Please set the environment variable:")
        print("export GEMINI_API_KEY='your_api_key_here'")
        return False
    
    print(f"✅ GEMINI_API_KEY is set: {api_key[:10]}...")
    
    # Test cases
    test_cases = [
        "会議の準備",
        "コードレビュー",
        "バグ修正",
        "資料作成",
        "テスト実行"
    ]
    
    print("\n=== Testing Description Generation ===")
    for title in test_cases:
        try:
            description = generate_description(title)
            print(f"✅ '{title}' → '{description}'")
        except Exception as e:
            print(f"❌ '{title}' → Error: {e}")
            return False
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    test_gemini_api()