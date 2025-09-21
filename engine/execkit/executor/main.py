import os.path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from rpa_executor.start import start

if __name__ == "__main__":
    start()
