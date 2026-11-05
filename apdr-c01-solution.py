import hashlib
import os 

SIGNATURES = {
    #for this problem honestly I used claude, but not in other one
    "PNG":  [b"\x89PNG\r\n\x1a\n"],
    "JPEG": [b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1"],
    "GIF":  [b"GIF87a", b"GIF89a"],
    "BMP":  [b"BM"],
    "TIFF": [b"II*\x00", b"MM\x00*"],          
    "ICO":  [b"\x00\x00\x01\x00"],
    "PSD":  [b"8BPS"],
    "PDF":  [b"%PDF-"],
    "OLE2": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],  
    "SQLITE": [b"SQLite format 3\x00"],
    "ZIP_FAMILY": [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"],  
    "DOCX": [b"PK\x03\x04"],
    "XLSX": [b"PK\x03\x04"],
    "PPTX": [b"PK\x03\x04"],
    "JAR": [b"PK\x03\x04"],
    "GZIP": [b"\x1f\x8b"],
    "BZIP2": [b"BZh"],
    "XZ":   [b"\xfd7zXZ\x00"],
    "7Z":   [b"7z\xbc\xaf\x27\x1c"],
    "RAR":  [b"Rar!\x1a\x07\x00", b"Rar!\x1a\x07\x01\x00"],  
    "ZSTD": [b"\x28\xb5\x2f\xfd"],
    "RIFF": [b"RIFF"],      
    "OGG":  [b"OggS"],
    "FLAC": [b"fLaC"],
    "MP3_ID3": [b"ID3"],    
    "ELF":  [b"\x7fELF"],
    "PE":   [b"MZ"],        
    "JAVA_CLASS": [b"\xca\xfe\xba\xbe"],
    "WASM": [b"\x00asm"],
}

def read_magic_bytes(filepath, n=16):
    with open(filepath, 'rb') as f:
        data = f.read(n)
        return data 
#########################TIGHT TIGHT TIGHT BLUE YELLOW PINK LET HIM COOK 
ZIP_SUBTYPES = (
    (b"AndroidManifest.xml", "APK"),
    (b"mimetypeapplication/epub+zip", "EPUB"),
    (b"word/", "DOCX"),
    (b"xl/", "XLSX"),
    (b"ppt/", "PPTX"),
    (b"META-INF/", "JAR"),)
def _zip_subtype(d): return next((k for m, k in ZIP_SUBTYPES if m in d), "ZIP_FAMILY")
def identify_file_type(magic):
    for name, sigs in SIGNATURES.items():
        if magic.startswith(tuple(sigs)):
            return _zip_subtype(magic) if name == "ZIP_FAMILY" else name
    return "unknown"
#####################################################################
def compute_checksum(filepath, algo="sha256"):
    digest = hashlib.new(algo)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()

def verify_integrity(filepath, expected_checksum, algo="sha256"):
    return compute_checksum(filepath, algo) == expected_checksum

###########internal!!!!!###### of tesk 5
def _claimed_file_type(filepath):
    return os.path.splitext(filepath)[1][1:].upper()
def _recurse_on_root(root_dir):
    paths = []
    for dirpath, dirname, filenames in os.walk(root_dir):
        for file in filenames:
            path = os.path.join(dirpath, file)
            paths.append(path)
    return paths # 대충대충 파일 패스 list 로 뭐.... 음... 스트링으로 뱉겠지???
def _actual_type(filepath):
    magic = read_magic_bytes(filepath, None)
    return identify_file_type(magic)
############Fianlly exteranl!!!!!!!##############
def find_mismatched_extensions(root_dir):
    extension_types = {
        "JPG": "JPEG",
        "TIF": "TIFF",
        "ZIP": "ZIP_FAMILY",
    }
    mismatches = []
    for path in _recurse_on_root(root_dir):
        claimed_type = _claimed_file_type(path)
        actual_type = _actual_type(path)
        if actual_type == "unknown":
            continue
        claimed_type = extension_types.get(claimed_type, claimed_type)
        if claimed_type != actual_type:
            mismatches.append({
                "path": path,
                "claimed_type": claimed_type,
                "actual_type": actual_type,
            })
    return mismatches

######################internalllllalalalalalllallallall#################
def _find_hidden_formats(filepath):
    found = []
    size = os.path.getsize(filepath)
    with open(filepath, "rb") as f:
        head = f.read(1024)                 
        f.seek(max(0, size - 65557))      
        tail = f.read()
    if b"%PDF-" in head:
        found.append("PDF")
    if b"PK\x05\x06" in tail:               
        found.append("ZIP")
    return found
##################thank you for this hard work^^^^^^^^^^^###########external
def detect_polyglot(filepath):
    formats = []
    actual_type = identify_file_type(read_magic_bytes(filepath, None))
    if actual_type != "unknown":
        formats.append(actual_type)
    for hidden_type in _find_hidden_formats(filepath):
        if hidden_type not in formats:
            formats.append(hidden_type)
    return formats

def bytes_to_hexdump(data, width=16):
    lines = []                                       
    for off in range(0, len(data), width):             # the only coding in this exercise !!!! wow 
        chunk = data[off:off + width]                  
        offset_part = f"{off:08X}" #00000016                     
        hex_part = " ".join(f"{b:02X}" for b in chunk) #hex you know...
        hex_part = hex_part.ljust(width * 3 - 1)# claude helped me lol but it works anyway       
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)#. or ascii 
        lines.append(f"{offset_part}  {hex_part}  |{ascii_part}|")
    return "\n".join(lines) 

def detect_text_encoding(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    if data.startswith(b"\xef\xbb\xbf"):
        return "UTF-8"
    if data.startswith(b"\xff\xfe"):
        return "UTF-16-LE"
    if data.startswith(b"\xfe\xff"):
        return "UTF-16-BE"
    if all(byte < 0x80 for byte in data):
        return "ASCII"
    try:
        data.decode("utf-8")
        return "UTF-8"
    except UnicodeDecodeError:
        return "Latin-1"
    
def find_appended_data(filepath, filetype):
    if filetype != "PNG":
        return None
    data = read_magic_bytes(filepath, None)
    pos = 8
    while pos + 12 <= len(data):
        n = int.from_bytes(data[pos:pos+4], "big")
        ctype = data[pos+4:pos+8]
        pos += 12 + n
        if ctype == b"IEND":
            return pos if pos < len(data) else None
    return None

def generate_forensics_report(root_dir):
    files = []
    findings = []
    mismatches = {
        item["path"]: item for item in find_mismatched_extensions(root_dir)
    }
    for path in _recurse_on_root(root_dir):
        file_type = _actual_type(path)
        files.append({
            "path": path,
            "file_type": file_type,
            "checksum": compute_checksum(path),
        })
        if path in mismatches:
            findings.append({
                "type": "mismatched_extension",
                **mismatches[path],
            })
        appended_offset = find_appended_data(path, file_type)
        if appended_offset is not None:
            findings.append({
                "type": "appended_data",
                "path": path,
                "offset": appended_offset,
            })
    return {"root": os.fspath(root_dir), "files": files, "findings": findings}
