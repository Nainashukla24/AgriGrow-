#!/usr/bin/env python3
"""
Run script for Agrigrow application.
This script provides a convenient way to start the Agrigrow application
with a single command from VS Code.
"""

import os
import sys
from app import app

def main():
    """Run the Agrigrow application."""
    print("Starting Agrigrow application...")
    print("Access the application at: http://127.0.0.1:8081")
    app.run(debug=True, port=8081)

if __name__ == "__main__":
    main()
