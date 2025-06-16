import subprocess
import sys
import os

def main():
    """Run the multi-agent news analysis system"""
    try:
        # Check if .env file exists
        if not os.path.exists('.env'):
            print("⚠️  Warning: .env file not found!")
            print("Please copy .env.example to .env and add your API keys.")
            return
        
        print("🚀 Starting Multi-Agent News Analysis System...")
        print("📱 Opening Streamlit interface...")
        
        # Run streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
