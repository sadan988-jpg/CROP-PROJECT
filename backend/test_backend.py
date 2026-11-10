import sys, os

# Add project root to sys.path
project_root = r"C:/Users/Sadan A/Downloads/crop project/backend"
sys.path.append(project_root)

try:
    from app.analytics.engine import process_image
    from app.utils.exif import extract_gps
except Exception as e:
    print('Import error:', e)
    sys.exit(1)

# Paths to the two uploaded sample images
image_paths = [
    r"C:/Users/Sadan A/.gemini/antigravity/brain/9f9c1858-5385-42c9-a53a-5597fd65e610/.user_uploaded/media_1794297030553_6a621228.png",
    r"C:/Users/Sadan A/.gemini/antigravity/brain/9f9c1858-5385-42c9-a53a-5597fd65e610/.user_uploaded/media_1794297046891_b9a58efc.jpg",
]

for path in image_paths:
    if not os.path.exists(path):
        print('File not found:', path)
        continue
    with open(path, 'rb') as f:
        img_bytes = f.read()
    # Run analytics
    result = process_image(img_bytes)
    print('--- Result for', os.path.basename(path), '---')
    print('Severity (%):', result['severity'])
    print('Disease prediction:', result['disease'])
    # GPS extraction
    gps = extract_gps(img_bytes)
    print('GPS data:', gps)
    print('Mask base64 size:', len(result['mask_base64']))
    print()

