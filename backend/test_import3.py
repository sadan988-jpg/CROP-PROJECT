import sys, os, pathlib
path = r"C:/Users/Sadan A/Downloads/crop project/backend"
print('Adding path:', path)
sys.path.append(path)
print('sys.path contains:', any('app' in p for p in sys.path))
print('Listing backend folder:')
print(os.listdir(path))
print('Checking app folder exists:')
app_path = os.path.join(path, 'app')
print('Exists?', os.path.isdir(app_path))
print('Contents:', os.listdir(app_path) if os.path.isdir(app_path) else 'N/A')

