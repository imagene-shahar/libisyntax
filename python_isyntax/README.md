# python-isyntax

Pythonic wrapper around the libisyntax C library.

```
from python_isyntax import Isyntax

with Isyntax("sample.isyntax") as img:
    print("Levels:", img.level_count, img.level_dimensions)
    region = img.read_region((0, 0), level=1, size=(512, 512))
    region.save("patch.png")
    thumb = img.get_thumbnail((256, 256))
    thumb.show()
```
