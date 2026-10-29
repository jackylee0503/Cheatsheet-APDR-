# APDR C01 Cheat Sheet — Tasks 1–9 (EN)

## 0. Basics you use in every task

No finished solutions here: each task lists the syntax and the traps, you assemble it. Stuck? Bring the function name and the exact error.

| What | Example | Result / gotcha |
| --- | --- | --- |
| Open as binary | `with open(path, "rb") as f:` | Without `"rb"` you get `str` and everything breaks. `with` closes the file for you |
| Byte literal | `b"\x89PNG"` | `\xNN` = one byte in hex. ASCII chars can be mixed in: `b"PK"` |
| Indexing | `data[0]` | Returns an **int** (`0x89` → 137). Out of range → IndexError |
| Slicing | `data[0:4]` | Returns **bytes**. Out of range does not crash, it just comes back shorter |
| Prefix check | `data.startswith(b"%PDF")` | Also takes a tuple: `data.startswith((b"A", b"B"))` |
| Contains / position | `b"IEND" in data`, `data.find(b"IEND")` | `find` returns **-1** if missing (no exception). From the end: `rfind` |
| Hex string ↔ bytes | `bytes.fromhex("89504e47")`, `data.hex(" ")` | For eyeballing while debugging |
| Bytes → int | `int.from_bytes(data[0:4], "big")` | Pick the endianness right: PNG is big, ZIP is little |
| Dict iteration | `for name, sigs in SIGNATURES.items():` | If the value is a list, loop over it again inside |
| Exceptions | `try: ... except OSError: ...` | For files that cannot be opened. Needed wherever the task says "must not crash" |

### What `\x00` actually is

A file is just a run of numbers 0–255. When Python prints bytes, it shows a byte as a character if it is printable ASCII, otherwise as `\x` + two hex digits. So `b"ABC\x00Z"` is **5 numbers**, not a string: `list(b"ABC\x00Z")` → `[65, 66, 67, 0, 90]`, `len(...)` → 5. `b"A" == b"\x41"` is True; `A` is just displayed nicely.

### Making bytes human-readable

| Want | Code | Output for `b"\x89PNG\r\n\x1a\n"` |
| --- | --- | --- |
| Hex (most useful) | `data.hex(" ")` | `89 50 4e 47 0d 0a 1a 0a` |
| Decimal | `list(data)` | `[137, 80, 78, 71, 13, 10, 26, 10]` |
| Bits | `format(b, "08b")` or `bin(b)` | `10001001` |
| ASCII view (hexdump right column) | `"".join(chr(b) if 32 <= b < 127 else "." for b in data)` | `.PNG....` |

Hex for exact values (lengths, endianness, `\x00`), ASCII view for spotting markers like `PNG`, `IHDR`, `IEND`, `%PDF`, `word/`, `PK` at odd offsets.

### str vs bytes

- `b"\xef"` = one byte with value 239. `"\xef"` = the character `ï` (U+00EF); `"\xef".encode()` → `b'\xc3\xaf'` (2 bytes). Mojibake usually comes from mixing these up.
- `str.encode("utf-8")` → bytes, `bytes.decode("utf-8")` → str.
- `bytes` is immutable. To modify, use `bytearray(data)`, then `ba[2] = 0x9d`.
- `open(path, encoding="utf-8-sig")` strips a UTF-8 BOM (`\xef\xbb\xbf`) when reading text.

### Notes for C programmers

- `bytes` ≈ `const unsigned char[]` that knows its length; `data[i]` is already unsigned (0–255), no sign extension.
- `int.from_bytes(b, "big")` replaces manual `(b[0] << 24) | (b[1] << 16) | ...`. `struct.unpack(">I", b)` is the closest thing to casting a header struct.
- Precedence is **opposite to C**: in Python `&` binds tighter than `==`, so `b & 0xE0 == 0xC0` means `(b & 0xE0) == 0xC0`. Write the parentheses anyway for readability.
- Slices never segfault or read past the end; they silently return fewer bytes. Check `len()` when the length matters.

## Tasks 1–3: read magic bytes and identify the type

### 1. read\_magic\_bytes

- `f.read(n)` reads **at most** n bytes. A shorter file just returns what it has, so the "must not crash on short files" case is free.
- "Don't load the whole file" = don't call `f.read()` with no argument here.
- Later tasks (9) need the whole file. If your function allows it, `read_magic_bytes(path, None)` reads everything; the default 16 will cut chunk data off.

### 2. SIGNATURES table

Shape: `{"FORMAT": [sig1, sig2, ...]}`. Values are lists because some formats (JPEG) have several variants.

| Format | Starting bytes | Note |
| --- | --- | --- |
| PNG | `\x89PNG\r\n\x1a\n` | 8 bytes |
| JPEG | `\xff\xd8\xff` + `\xe0` / `\xe1` / `\xdb` / `\xee` | 4th byte = variant (JFIF, Exif, raw…) |
| GIF | `GIF87a`, `GIF89a` | Two versions |
| PDF | `%PDF-` |  |
| ZIP family | `PK\x03\x04` | docx/xlsx/pptx/jar all start with this |
| GZIP | `\x1f\x8b` |  |
| BMP | `BM` | Only 2 bytes, false positives → check late |
| ELF | `\x7fELF` | Linux executable |
| PE/EXE | `MZ` | Windows executable, also 2 bytes |
| WAV | `RIFF` + `WAVE` at offset 8 | `RIFF` is also used by AVI/WEBP |
| MP3 | `ID3` | Untagged MP3: `\xff\xfb` |
| 7z | `7z\xbc\xaf\x27\x1c` |  |
| RAR | `Rar!\x1a\x07` |  |
| TIFF | `II*\x00`, `MM\x00*` | Little / big endian |
| SQLite | `SQLite format 3\x00` | Exactly 16 bytes |

Working with a dict of lists:

- `SIGNATURES["JPEG"].hex(" ")` → AttributeError (a list has no `.hex`). Index first: `SIGNATURES["JPEG"][0].hex(" ")` → `'ff d8 ff e0'`.
- Match any variant without an inner loop: `data.startswith(tuple(sigs))`. Passing the list itself raises TypeError; it must be a `tuple`.

### 3. identify\_file\_type (incl. telling ZIP-family apart)

- 16 bytes can't tell what is inside a ZIP. You need a few KB; how much `magic` you pass in is your design choice.
- Inner file paths sit in plain text inside the archive bytes: docx → `b"word/"` · xlsx → `b"xl/"` · pptx → `b"ppt/"` · jar → `b"META-INF/"`. Check with `b"word/" in data`.
- Optional, exact: first filename from the local header. Name length = `int.from_bytes(data[26:28], "little")`, name = `data[30:30+length]`.
- Order matters: specific signatures first, short/generic ones (`MZ`, `BM`) last. `return` on the first match.
- Nothing matched → `return "unknown"` after the loop.
- Mid-file checks like RIFF: `data[8:12] == b"WAVE"` (safe even on short files).
- The public test compares `identify_file_type(...) == "PNG"` **exactly**, no `.upper()`. Return uppercase names.

## Tasks 4–5: hashing and walking folders

### 4. compute\_checksum / verify\_integrity

- `import hashlib`
- The algorithm comes in as a string, so `h = hashlib.new(algo)` (don't hardcode `hashlib.sha256()`).
- Feed big files in chunks: calling `h.update(chunk)` repeatedly continues the same hash.
- Chunk loop, pick one:
  - `while chunk := f.read(8192):` (walrus operator: read, stop when empty)
  - `for chunk in iter(lambda: f.read(8192), b""):`
- Result: `h.hexdigest()` → lowercase hex string.
- verify: plain `==`. Wrap the expected value in `.lower()` in case it arrives uppercase.

### 5. find\_mismatched\_extensions

Recursive walk, pick one style and don't mix:

- `pathlib`: `for p in Path(root_dir).rglob("*"):` + `if p.is_file():`. Already full paths; join with `Path("samples") / "a.png"`.
- `os`: `for dirpath, dirnames, filenames in os.walk(root_dir):`. `filenames` are **bare names**, so build the path with `os.path.join(dirpath, name)`. `open(name)` alone → FileNotFoundError.

`os` vs `os.path`:

| Module | Does | Functions useful here |
| --- | --- | --- |
| `os` | Tells the OS to do things | `walk`, `listdir` |
| `os.path` (string-only) | Builds and splits path strings, touches no file | `join`, `splitext` (`"a.tar.gz"` → `('a.tar', '.gz')`), `basename`, `dirname` |
| `os.path` (disk lookup) | Asks about a file on disk | `getsize` (tasks 6, 9), `isfile`, `exists` |

`os.path` is actually `posixpath` on Linux/macOS and `ntpath` on Windows, which is why `join` uses the right separator.

Recommended helper, since tasks 5, 6, 9 and 10 all loop over every file (extra helper functions are fine, the grader only imports the required names):

```python
def list_all_files(root_dir):
    paths = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for name in filenames:
            paths.append(os.path.join(dirpath, name))  # full path, not just name
    return paths
```

Rest of task 5:

- Extension: `os.path.splitext(path)[1].lower()` or `p.suffix.lower()` → `".jpg"` (dot included).
- Separate mapping dict: `{".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ...}`. Names must match your SIGNATURES keys exactly, or the comparison fails.
- Collect: `results.append({"path": str(p), "claimed_type": ..., "actual_type": ...})`.
- Use `str(p)`, not a `Path` object; it breaks JSON serialization in task 10.
- What the public test checks: keys `path`, `claimed_type`, `actual_type` (exact lowercase key names); `actual_type` compared with `.upper()`; `claimed_type` value not checked; a correct `image.png` must **not** be reported.
- Use uppercase for both types anyway, so `claimed != actual` works. If casing differs, correct files get flagged and the second test fails.
- Unknown extensions (e.g. `invoice.txt`): `"TXT"` or `None` both pass. With `None`, check it becomes `null` in task 10's JSON.

## Tasks 6–7: polyglots and hexdump

### 6. detect\_polyglot

A polyglot is one file that is valid as two or more formats at once. It works because formats look at **different places** in the file:

- **PDF**: the reader looks for `%PDF-` anywhere in the first 1024 bytes, not only at offset 0.
- **ZIP**: read **from the end**. The reader finds `PK\x05\x06` (End of Central Directory, EOCD) near the end and follows it; whatever sits in front is ignored.

So `[PDF bytes][ZIP bytes]` opens fine in both. The public test builds exactly that: `pdf_prefix + make_zip_bytes()`. Reading only the start gives `["PDF"]` and never finds the ZIP, so start-only detection cannot work by definition.

|  | Task 3 identify\_file\_type | Task 6 detect\_polyglot |
| --- | --- | --- |
| Returns | One string (`"PNG"`) | A list (`["PDF", "ZIP"]`) |
| Looks at | Start bytes only | Start + head window + tail |
| Matching | `return` on first hit | `append` every hit, no early return |

Syntax you need:

- Collect all: `matches = []` + `append`, or a list comprehension `[name for name, sigs in ... if ...]`.
- Dedupe: `list(set(matches))`, then `sorted(...)` if order matters.
- PDF in head: `b"%PDF-" in data[:1024]`.
- Tail read: `f.seek(offset)` then `f.read()`. The EOCD is at most 22 + 65535 bytes from the end, so `f.seek(max(0, size - 65557))` covers every case. `f.seek(-n, 2)` (2 = from end) errors if the file is shorter than n, hence the `max(0, ...)`.
- File size: `os.path.getsize(path)`, or `f.seek(0, 2)` then `f.tell()`.
- **Trap:** normal docx/xlsx/pptx/jar are ZIPs inside, so the tail check finds `"ZIP"` too. If the main type is already ZIP-family, drop the extra `"ZIP"`, or a clean .docx gets reported as a polyglot. Not in the public tests; likely in hidden ones.
- The public test accepts either `"ZIP"` or `"ZIP_FAMILY"` for the ZIP part.

### 7. bytes\_to\_hexdump

**width = how many bytes per line.** Default 16; the public test calls it with 4. The function returns **one string**. The format is defined by the test, not by `hexdump -C`. Expected output for `data = b"ABC\x00Z"`, `width=4`:

```
00000000  41 42 43 00  |ABC.|
00000004  5A           |Z|
```

| Column | Content | Example |
| --- | --- | --- |
| Offset | Position of the line's first byte, 8 hex digits | `00000000`, then `00000004` (steps by width) |
| 2 spaces |  |  |
| Hex | Each byte as 2 hex digits, space-separated, fixed width | `41 42 43 00` |
| 2 spaces |  |  |
| ASCII | Same bytes as chars, non-printable → `.` | `\|ABC.\|` |

Syntax:

- Split into lines: `for off in range(0, len(data), width):` → `chunk = data[off:off+width]`.
- Hex is **uppercase**: `f"{b:02X}"` (test has `5A`), then `" ".join(...)`.
- Offset: `f"{off:08X}"`. Casing unconfirmed (no A–F offsets in the test); uppercase to match the hex.
- Hex column width is always `width * 3 - 1`; pad the short last line with `.ljust(width * 3 - 1)` so `|Z|` lines up with `|ABC.|`.
- ASCII column has no padding (`|Z|`): `chr(b) if 32 <= b < 127 else "."`.
- No extra gap every 8 bytes, no trailing total-length line, no trailing newline.
- Join lines: `"\n".join(lines)`.
- Build this one early: it is the debugging tool for every other task.

## Tasks 8–9: encoding detection and appended data

### 8. detect\_text\_encoding

The check order is the whole structure: **BOM → ASCII → UTF-8 → otherwise Latin-1**. Latin-1 accepts every byte, so it is always the last fallback.

| Verdict | Byte pattern |
| --- | --- |
| UTF-8 BOM | Starts with `\xef\xbb\xbf` |
| UTF-16-LE BOM | Starts with `\xff\xfe` |
| UTF-16-BE BOM | Starts with `\xfe\xff` |
| ASCII | Every byte < 0x80: `all(b < 0x80 for b in data)` |
| UTF-8 (no BOM) | All multi-byte rules hold (below) |
| UTF-16 (no BOM) | English text puts `\x00` on every other byte: compare `data[1::2].count(0)` vs `data[0::2].count(0)` |

UTF-8 in one picture: a character is 1–4 bytes. The **lead byte** says how many bytes the group has; every **follower** must be in `0x80–0xBF`.

| Lead byte bits | Mask check | Group size | Example |
| --- | --- | --- | --- |
| `0xxxxxxx` | `(b & 0x80) == 0x00` | 1 (plain ASCII) | `A` = `41` |
| `110xxxxx` | `(b & 0xE0) == 0xC0` | 2 | `ü` = `C3 BC` |
| `1110xxxx` | `(b & 0xF0) == 0xE0` | 3 | `한` = `ED 95 9C` |
| `11110xxx` | `(b & 0xF8) == 0xF0` | 4 | emoji |
| `10xxxxxx` (follower) | `(c & 0xC0) == 0x80` | never alone | `BC` |

`&` keeps only the top bits: `0xC3 & 0xE0` → `0xC0`, so `C3` is a 2-byte lead.

- Walk with an index you control: `i = 0` + `while i < len(data):` + `i += group_size`.
- Any broken follower, a stray follower, or data ending mid-group → not UTF-8. Latin-1 `ü` is the single byte `FC` (`11111100`), which matches no row, so it fails fast.
- Shortcut: `try: data.decode("utf-8")` / `except UnicodeDecodeError:` does the same check for you. It may clash with a "don't use automatic detection" rule; the public tests can't tell the difference, so the manual check is the safe version.

### 9. find\_appended\_data

Rule: **compute where the valid structure ends → equal to file size → `None`; smaller → return that offset.** This task needs the whole file (`f.read()` is fine here; the no-full-load rule was task 1 only).

| Format | End marker | End offset |
| --- | --- | --- |
| PNG | `IEND` chunk | Start of IEND chunk + 12 (length 4 + type 4 + CRC 4) |
| JPEG | `\xff\xd9` (EOI) | Position + 2. Thumbnails also contain FFD9, so the first one may not be the real end |
| GIF | `\x3b` (trailer) | Position + 1 |
| PDF | `%%EOF` | Position + 5 (decide whether a trailing `\n` / `\r\n` counts as normal) |
| ZIP | `PK\x05\x06` (EOCD) | Position + 22 + comment length `int.from_bytes(data[pos+20:pos+22], "little")` |

Walk PNG chunks instead of searching. `data.find(b"IEND")` is unsafe: compressed IDAT data can contain those 4 bytes by accident, and an appended payload can contain them too.

- Bytes 0–7: signature. Then chunks repeat until IEND.
- Chunk layout: `[length: 4 bytes, big-endian][type: 4 bytes][data: length bytes][CRC: 4 bytes]`.
- `length = int.from_bytes(data[pos:pos+4], "big")`, `ctype = data[pos+4:pos+8]`.
- Next chunk: `pos + 12 + length`. Loop with `while pos + 12 <= len(data):` until `ctype == b"IEND"`.
- Alternative: `import struct` → `struct.unpack(">I", data[pos:pos+4])[0]` (`>` = big-endian, `I` = 4-byte unsigned).
- Guard: if the file is not a PNG, bail out early, or you'll jump around using random bytes as lengths. Also handle "ran off the end without IEND" (broken file).

Why PNGs compress so well (context, not needed for the code): each row is prefixed with a filter byte and stores differences to the left or upper pixel, so flat images become mostly zeros before zlib. That is also why IDAT bytes look random.

For the README write-up (how you found the polyglot + exact payload offset): run tasks 6 and 9, then print the region with your task 7 hexdump as evidence.

## Debug routine and what the public tests check

Fastest loop: look at the real bytes, then run the tests.

```python
print(read_magic_bytes("samples/somefile").hex(" "))
print(bytes_to_hexdump(open("samples/somefile", "rb").read()[:64]))
```

```
python -m pytest -q tests/test_public.py
python -m pytest -v tests/test_public.py   # see which test fails, read its assert first
```

| Task | What the public test pins down |
| --- | --- |
| 3 | Exact string compare, e.g. `== "PNG"` (uppercase, no normalization) |
| 5 | Keys `path`, `claimed_type`, `actual_type`; `actual_type` compared via `.upper()`; correct files must not be listed |
| 6 | One-format file → one type; `pdf_prefix + zip` → both PDF and `ZIP` / `ZIP_FAMILY` |
| 7 | `width=4` output exactly as shown in section 7 (uppercase hex, fixed hex column, no trailing newline) |

The README says the current tests are structural only, so hidden tests may check more (casing of offsets, docx false positives in task 6, broken PNGs in task 9). Cover those edge cases even though public tests pass.
