#!/usr/bin/env python3
"""
Test script to verify Sentilytics Backend setup
"""
import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import motor
        print("✅ Motor (MongoDB) imported successfully")
    except ImportError as e:
        print(f"❌ Motor import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from app.config import settings
        print("✅ Configuration loaded successfully")
        print(f"   App Name: {settings.app_name}")
        print(f"   Version: {settings.app_version}")
        print(f"   Debug: {settings.debug}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_models():
    """Test Pydantic models"""
    print("\n📋 Testing models...")
    
    try:
        from app.models.sentiment import AnalysisRequest, SentimentType
        print("✅ Models imported successfully")
        
        # Test model creation
        request = AnalysisRequest(ticker="AAPL", max_posts=10)
        print(f"✅ Model creation successful: {request.ticker}")
        return True
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🌍 Testing environment...")
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found (copy from env.example)")
    
    # Check required environment variables
    required_vars = ["MONGODB_URI", "GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} is not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Please set these in your .env file")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Sentilytics Backend Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_models,
        test_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is ready to run.")
        print("\nNext steps:")
        print("1. Set up your .env file with API keys")
        print("2. Run: python run.py")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 