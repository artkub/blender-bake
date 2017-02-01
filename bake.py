import sys
import os
sys.path.append(os.path.dirname(__file__))
from bake_lib import import_bake_and_export, bake_and_export

if len(sys.argv) == 5:
    path = sys.argv[-1]
    print(path, os.path.isdir(path))
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith('.obj'):
                    import_bake_and_export(os.path.join(root, filename))
    else:
        import_bake_and_export(path)
else:
    bake_and_export('output', os.getcwd())

print('done')
