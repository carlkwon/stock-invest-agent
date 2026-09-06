import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'data'))
try:
    from krx_openapi_provider import get_kospi_daily_trade
    print("Successfully imported")
except Exception as e:
    print(f"Error: {e}")
