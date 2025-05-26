"""ctypes bindings for libisyntax."""

from __future__ import annotations

import ctypes
import os
from ctypes import c_int32, c_int64, c_uint32, c_char_p, c_float, POINTER


class LibISyntax:
    """Thin wrapper around the libisyntax shared library."""

    def __init__(self, library_path: str | None = None) -> None:
        if library_path is None:
            library_path = os.environ.get("LIBISYNTAX_PATH", "libisyntax.so")
        self.lib = ctypes.CDLL(library_path)
        self._setup()

    def _setup(self) -> None:
        lib = self.lib

        self.LIBISYNTAX_OK = 0
        self.LIBISYNTAX_FATAL = 1
        self.LIBISYNTAX_INVALID_ARGUMENT = 2

        lib.libisyntax_init.restype = c_int32

        lib.libisyntax_open.argtypes = [c_char_p, c_int32, POINTER(ctypes.c_void_p)]
        lib.libisyntax_open.restype = c_int32

        lib.libisyntax_close.argtypes = [ctypes.c_void_p]
        lib.libisyntax_close.restype = None

        lib.libisyntax_get_wsi_image.argtypes = [ctypes.c_void_p]
        lib.libisyntax_get_wsi_image.restype = ctypes.c_void_p

        lib.libisyntax_image_get_level_count.argtypes = [ctypes.c_void_p]
        lib.libisyntax_image_get_level_count.restype = c_int32

        lib.libisyntax_image_get_level.argtypes = [ctypes.c_void_p, c_int32]
        lib.libisyntax_image_get_level.restype = ctypes.c_void_p

        lib.libisyntax_level_get_width.argtypes = [ctypes.c_void_p]
        lib.libisyntax_level_get_width.restype = c_int32

        lib.libisyntax_level_get_height.argtypes = [ctypes.c_void_p]
        lib.libisyntax_level_get_height.restype = c_int32

        lib.libisyntax_read_region.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            c_int32,
            c_int64,
            c_int64,
            c_int64,
            c_int64,
            POINTER(c_uint32),
            c_int32,
        ]
        lib.libisyntax_read_region.restype = c_int32

        lib.libisyntax_read_label_image.argtypes = [
            ctypes.c_void_p,
            POINTER(c_int32),
            POINTER(c_int32),
            POINTER(POINTER(c_uint32)),
            c_int32,
        ]
        lib.libisyntax_read_label_image.restype = c_int32

        lib.libisyntax_read_macro_image.argtypes = [
            ctypes.c_void_p,
            POINTER(c_int32),
            POINTER(c_int32),
            POINTER(POINTER(c_uint32)),
            c_int32,
        ]
        lib.libisyntax_read_macro_image.restype = c_int32

        lib.libisyntax_get_tile_width.argtypes = [ctypes.c_void_p]
        lib.libisyntax_get_tile_width.restype = c_int32
        lib.libisyntax_get_tile_height.argtypes = [ctypes.c_void_p]
        lib.libisyntax_get_tile_height.restype = c_int32

        lib.libisyntax_cache_create.argtypes = [c_char_p, c_int32, POINTER(ctypes.c_void_p)]
        lib.libisyntax_cache_create.restype = c_int32

        lib.libisyntax_cache_inject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        lib.libisyntax_cache_inject.restype = c_int32

        lib.libisyntax_cache_destroy.argtypes = [ctypes.c_void_p]
        lib.libisyntax_cache_destroy.restype = None


LIB = LibISyntax()
