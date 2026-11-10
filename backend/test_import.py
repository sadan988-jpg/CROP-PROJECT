import sys, pathlib, os
sys.path.append(r"C:/Users/Sadan A/Downloads/crop project/backend")
try:
    from app.main import app
    print('Import succeeded')
except Exception as e:
    print('Import failed:', e)

