import sys, os
path = r"C:/Users/Sadan A/Downloads/crop project/backend"
print('Adding path:', path)
sys.path.append(path)
print('sys.path now contains app?', any('app' in p for p in sys.path))
try:
    from app.main import app
    print('Import succeeded')
except Exception as e:
    print('Import failed:', e)

