import sys, importlib
print('python', sys.version)
mods=['insightface','onnxruntime','cv2','customtkinter']
for m in mods:
    try:
        mod=importlib.import_module(m)
        v=getattr(mod,'__version__', None)
        if v:
            print(f"{m} version {v}")
        else:
            print(f"{m} imported")
    except Exception as e:
        print(f"{m} ERROR: {e}")

try:
    import onnxruntime as ort
    print('ONNX providers:', ort.get_available_providers())
except Exception as e:
    print('onnxruntime ERROR:', e)
