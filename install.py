import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is 3.6 or higher"""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)

def install_requirements():
    """Install required packages using pip"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\nInstallation successful! You can now run NFA_DFA_Converter.py")
    except subprocess.CalledProcessError as e:
        print(f"\nError installing packages: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

def main():
    print("NFA to DFA Converter - Installation")
    print("==================================")
    
    # Check Python version
    check_python_version()
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found")
        sys.exit(1)
    
    # Install requirements
    install_requirements()

if __name__ == "__main__":
    main() 