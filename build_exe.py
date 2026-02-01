import PyInstaller.__main__
import facebook_business
import os

# Find the location of the facebook_business package
fb_path = os.path.dirname(facebook_business.__file__)
crt_file = os.path.join(fb_path, 'fb_ca_chain_bundle.crt')

if not os.path.exists(crt_file):
    print(f"Error: Could not find Certificate file at {crt_file}")
    exit(1)

print(f"Found Facebook Certificate: {crt_file}")

# PyInstaller arguments
args = [
    'gui.py',
    '--name=FBAdsUploader',
    '--noconfirm',
    '--onefile',
    '--windowed',
    '--clean',
    # Add the CRT file to the facebook_business directory inside the exe
    f'--add-data={crt_file};facebook_business',
    # Ensure config is bundled/handled if we want it (implementation plan said next to exe, so we don't bundle it into the exe internal)
    # But wait, config.json is external, so we don't add-data it. App creates it.
]

print("Running PyInstaller with args:", args)

PyInstaller.__main__.run(args)
