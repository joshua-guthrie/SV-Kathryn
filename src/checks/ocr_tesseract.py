"""Small wrapper around the installed Tesseract C API; no Python OCR install.

Models are external inputs. Original OCR is retained separately from checked
transcriptions; confidence scores are engine output, not historical certainty.
"""
import ctypes as C
import ctypes.util
import os

os.environ.setdefault('OMP_THREAD_LIMIT', '1')


class Tesseract:
    def __init__(self, tessdata):
        self.lib = lib = C.CDLL(C.util.find_library('tesseract'))
        lib.TessVersion.restype = C.c_char_p
        lib.TessBaseAPICreate.restype = C.c_void_p
        lib.TessBaseAPIInit3.argtypes = [C.c_void_p, C.c_char_p, C.c_char_p]
        lib.TessBaseAPIInit3.restype = C.c_int
        lib.TessBaseAPISetPageSegMode.argtypes = [C.c_void_p, C.c_int]
        lib.TessBaseAPISetImage.argtypes = [C.c_void_p, C.c_void_p, C.c_int,
                                           C.c_int, C.c_int, C.c_int]
        lib.TessBaseAPISetSourceResolution.argtypes = [C.c_void_p, C.c_int]
        for method in ('TessBaseAPIGetUTF8Text', 'TessBaseAPIGetTsvText'):
            fn = getattr(lib, method)
            fn.restype = C.c_void_p
            fn.argtypes = [C.c_void_p] if 'UTF8' in method else [C.c_void_p, C.c_int]
        lib.TessDeleteText.argtypes = [C.c_void_p]
        lib.TessBaseAPIDelete.argtypes = [C.c_void_p]
        self.api = lib.TessBaseAPICreate()
        if lib.TessBaseAPIInit3(self.api, str(tessdata).encode(), b'eng'):
            self.close()
            raise RuntimeError('Tesseract could not load the English model')

    @property
    def version(self):
        return self.lib.TessVersion().decode()

    def text(self, pointer):
        if not pointer:
            return ''
        result = C.string_at(pointer).decode('utf-8', errors='replace')
        self.lib.TessDeleteText(pointer)
        return result

    def recognize(self, image, psm=3, dpi=400):
        image = image.convert('L')
        raw = C.create_string_buffer(image.tobytes())
        self.lib.TessBaseAPISetPageSegMode(self.api, psm)
        self.lib.TessBaseAPISetImage(self.api, raw, image.width, image.height, 1, image.width)
        self.lib.TessBaseAPISetSourceResolution(self.api, int(dpi))
        text = self.text(self.lib.TessBaseAPIGetUTF8Text(self.api))
        tsv = self.text(self.lib.TessBaseAPIGetTsvText(self.api, 0))
        return text, tsv

    def close(self):
        if getattr(self, 'api', None):
            self.lib.TessBaseAPIDelete(self.api)
            self.api = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
