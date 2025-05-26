"""High-level wrapper for libisyntax."""

from __future__ import annotations

import ctypes
from typing import Dict, List, Tuple
from PIL import Image

from .lib import LIB


class IsyntaxError(Exception):
    """Base exception for iSyntax errors."""


class Isyntax:
    """Represents an iSyntax whole-slide image."""

    def __init__(self, filename: str) -> None:
        self._filename = filename.encode()
        self._handle = ctypes.c_void_p()
        err = LIB.lib.libisyntax_init()
        if err != LIB.LIBISYNTAX_OK:
            raise IsyntaxError(f"libisyntax_init failed with code {err}")
        err = LIB.lib.libisyntax_open(self._filename, 0, ctypes.byref(self._handle))
        if err != LIB.LIBISYNTAX_OK:
            raise IsyntaxError(f"libisyntax_open failed with code {err}")
        self._cache = ctypes.c_void_p()
        LIB.lib.libisyntax_cache_create(None, 128, ctypes.byref(self._cache))
        LIB.lib.libisyntax_cache_inject(self._cache, self._handle)
        self._closed = False

        self._wsi_image = LIB.lib.libisyntax_get_wsi_image(self._handle)

    # Context manager -----------------------------------------------------
    def __enter__(self) -> "Isyntax":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        self.close()

    def __del__(self) -> None:  # noqa: D401
        self.close()

    # ---------------------------------------------------------------------
    def close(self) -> None:
        if not self._closed:
            if self._cache:
                LIB.lib.libisyntax_cache_destroy(self._cache)
                self._cache = ctypes.c_void_p()
            if self._handle:
                LIB.lib.libisyntax_close(self._handle)
                self._handle = ctypes.c_void_p()
            self._closed = True

    # Properties ----------------------------------------------------------
    @property
    def level_count(self) -> int:
        """Number of resolution levels."""
        return LIB.lib.libisyntax_image_get_level_count(self._wsi_image)

    @property
    def level_dimensions(self) -> List[Tuple[int, int]]:
        """Dimensions for all levels."""
        dims = []
        for i in range(self.level_count):
            level = LIB.lib.libisyntax_image_get_level(self._wsi_image, i)
            width = LIB.lib.libisyntax_level_get_width(level)
            height = LIB.lib.libisyntax_level_get_height(level)
            dims.append((width, height))
        return dims

    @property
    def properties(self) -> Dict[str, str]:
        """Dictionary of slide properties."""
        # libisyntax does not yet expose metadata via API; return minimal stub
        return {"vendor": "Philips", "filename": self._filename.decode()}

    @property
    def associated_images(self) -> Dict[str, Image.Image]:
        """Return associated images such as label and macro."""
        images: Dict[str, Image.Image] = {}
        width = ctypes.c_int32()
        height = ctypes.c_int32()
        buf = ctypes.POINTER(ctypes.c_uint32)()
        err = LIB.lib.libisyntax_read_label_image(self._handle, ctypes.byref(width), ctypes.byref(height), ctypes.byref(buf), 1)
        if err == LIB.LIBISYNTAX_OK:
            data = ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint32 * (width.value * height.value))).contents
            img = Image.frombuffer("RGBA", (width.value, height.value), data, "raw", "BGRA", 0, 1)
            images["label"] = img
        err = LIB.lib.libisyntax_read_macro_image(self._handle, ctypes.byref(width), ctypes.byref(height), ctypes.byref(buf), 1)
        if err == LIB.LIBISYNTAX_OK:
            data = ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint32 * (width.value * height.value))).contents
            img = Image.frombuffer("RGBA", (width.value, height.value), data, "raw", "BGRA", 0, 1)
            images["macro"] = img
        return images

    # Methods -------------------------------------------------------------
    def read_region(self, location: Tuple[int, int], level: int, size: Tuple[int, int]) -> Image.Image:
        """Read an image region.

        Args:
            location: (x, y) tuple in level 0 reference frame.
            level: Resolution level index.
            size: (width, height) of region to extract.

        Returns:
            PIL Image containing the requested region.
        """
        x, y = location
        width, height = size
        buffer_size = width * height
        buf = (ctypes.c_uint32 * buffer_size)()
        err = LIB.lib.libisyntax_read_region(
            self._handle,
            self._cache,
            level,
            x,
            y,
            width,
            height,
            buf,
            1,
        )
        if err != LIB.LIBISYNTAX_OK:
            raise IsyntaxError(f"read_region failed with code {err}")
        data = bytes(buf)
        img = Image.frombuffer("RGBA", (width, height), data, "raw", "BGRA", 0, 1)
        return img

    def get_thumbnail(self, size: Tuple[int, int]) -> Image.Image:
        """Return thumbnail image of approximate size."""
        best_level = self.get_best_level_for_downsample(max(self.level_dimensions[0][0] / size[0], 1))
        dims = self.level_dimensions[best_level]
        thumb = self.read_region((0, 0), best_level, dims)
        thumb.thumbnail(size)
        return thumb

    def get_best_level_for_downsample(self, downsample: float) -> int:
        """Choose the best level for a given downsample factor."""
        for i, dim in enumerate(self.level_dimensions):
            level_downsample = self.level_dimensions[0][0] / dim[0]
            if level_downsample >= downsample:
                return i
        return self.level_count - 1
