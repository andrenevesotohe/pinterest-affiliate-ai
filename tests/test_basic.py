def test_imports():
    """Test that we can import our main modules."""
    try:
        import modules.poster
        assert True
    except ImportError:
        assert False, "Failed to import modules.poster"

def test_environment():
    """Test that our environment is set up correctly."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Check that required environment variables are defined
    required_vars = [
        'OPENAI_API_KEY',
        'PINTEREST_ACCESS_TOKEN',
        'AMAZON_ASSOCIATE_TAG'
    ]
    
    for var in required_vars:
        assert var in os.environ, f"Missing environment variable: {var}" 