#!/usr/bin/env python3
"""
Setup script for Second-Hand Trading Platform
Run this script to set up the project for development or production.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        'static/uploads',
        'static/avatars',
        'instance'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def create_database():
    """Create the database and tables."""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database created successfully")
        return True
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path('.env')
    if not env_file.exists():
        import secrets
        secret_key = secrets.token_hex(32)
        
        with open('.env', 'w') as f:
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write("FLASK_ENV=development\n")
        
        print("✅ Created .env file with generated secret key")
    else:
        print("ℹ️  .env file already exists")

def main():
    """Main setup function."""
    print("🚀 Setting up Second-Hand Trading Platform...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create database
    if not create_database():
        print("❌ Setup failed at database creation")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the application: python app.py")
    print("2. Open your browser to: http://127.0.0.1:5000")
    print("3. Register a new user account")
    print("4. Start using the platform!")
    print("\n📚 Documentation:")
    print("- README.md: Project overview and features")
    print("- DEPLOYMENT.md: Production deployment guide")
    print("- PROJECT_STRUCTURE.md: Detailed project structure")

if __name__ == "__main__":
    main() 