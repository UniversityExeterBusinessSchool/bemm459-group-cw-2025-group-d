# Project/UseCase/__init__.py
# This file is neccessary to make python recognize this folder as package.
# So you can import file from this directory to other directory.
import sys
import os

# Add the Project directory to sys.path
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Now, you can use absolute imports
from env import postgreSQL_host