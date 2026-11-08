# APDR Ch. 6.3 Endianness — Study Notes (EN / KO)

Each section gives the English first, then the Korean. Exercises get the approach only, no finished solutions.
각 섹션은 영어 먼저, 그다음 한국어야. 연습문제는 접근법만 있고 완성된 풀이는 없어.

---

## 0. Big picture / 큰 그림

**EN** — When a multi-byte integer is stored, which byte goes at the lowest address? That choice is endianness. Byte addressing (6.2) means a 4-byte int occupies four addresses, so the order of its four bytes must be decided separately.

**KO** — 여러 바이트짜리 정수를 메모리에 놓을 때 어느 바이트를 가장 낮은 주소에 두나. 그 답이 endianness야. 6.2에서 주소 하나가 1바이트라고 했으니까, 4바이트 int는 주소 4칸을 차지하고 그 4바이트의 순서는 따로 정해야 해.

- **MSB** (most significant byte): highest place value / 자릿값이 가장 큰 바이트 — `0x12` in `0x12345678`
- **LSB** (least significant byte): lowest place value / 자릿값이 가장 작은 바이트 — `0x78` in `0x12345678`
- Two hex digits = one byte (16 × 16 = 256 = 2^8). / 16진수 두 자리가 딱 1바이트.

| Part / 파트 | One line / 한 줄 요약 | Exam point / 시험 포인트 |
| --- | --- | --- |
| Big vs little | MSB first or LSB first / MSB가 앞이냐 LSB가 앞이냐 | write the byte layout / 바이트 배치 쓰기 |
| Why it matters / 왜 중요한가 | only at boundaries between machines / 머신 경계를 넘을 때만 문제 | when to care / 언제 신경 써야 하나 |
| Worked example | same 4 bytes = 456 or 3.3 billion / 같은 4바이트가 456도 되고 33억도 됨 | bytes → int / 바이트 → 정수 계산 |
| Conversion cost / 변환 비용 | one swap is free, millions are not / 하나는 공짜, 대량은 아님 | concept only / 개념만 |

---

## 1. Big-endian vs little-endian

Example: `0x54BCFE30` stored from address 24. / 예제: `0x54BCFE30`을 주소 24부터 저장.

| Address / 주소 | big-endian | little-endian |
| --- | --- | --- |
| 24 | `0x54` (MSB) | `0x30` (LSB) |
| 25 | `0xBC` | `0xFE` |
| 26 | `0xFE` | `0xBC` |
| 27 | `0x30` (LSB) | `0x54` (MSB) |

**EN** — The name says what comes first at the lowest address: big end first = big-endian, little end first = little-endian. The value is the same either way; only the placement differs. Only bytes are reordered: bits inside a byte and hex digits (nibbles) stay put (`0x30` never becomes `0x03`).

**KO** — 이름은 낮은 주소에 뭐가 먼저 오나 기준이야. big이 먼저면 big-endian, little이 먼저면 little-endian. 값은 같고 놓는 순서만 달라. 뒤집히는 건 바이트 단위뿐이고, 바이트 안의 비트나 16진수 자리(니블)는 안 뒤집혀 (`0x30`은 `0x03`이 되지 않아).

| Order / 방식 | Architectures / 아키텍처 |
| --- | --- |
| big-endian | Motorola 68000, IBM System/360 family, SPARC (mostly historical / 주로 옛날) |
| little-endian | x86, x86-64 (most PCs and servers today / 지금 PC·서버 대부분) |
| bi-endian | ARM: configurable at boot, almost always little in practice / 부팅 때 고를 수 있지만 거의 little |

**EN** — The names come from *Gulliver's Travels*: two factions fight over which end of an egg to crack. Neither is inherently better.
**KO** — 이름은 《걸리버 여행기》에서 왔어. 달걀을 어느 쪽부터 깨느냐로 싸우는 두 파벌 얘기야. 어느 쪽도 본질적으로 더 낫지 않다는 농담이지.

---

## 2. Why it matters / 왜 중요한가

**EN** — Inside one machine endianness is invisible: load and store use the same convention, so a value written and read back is unchanged. Problems appear only when bytes cross a boundary with a different convention.

**KO** — 머신 하나 안에서는 안 보여. load/store가 같은 규칙으로 쓰고 읽으니까 저장했다 읽으면 원래 값이 나와. 문제는 바이트가 규칙이 다른 곳으로 넘어갈 때뿐이야.

| Case / 상황 | What happens / 무슨 일 | Fix / 해결 |
| --- | --- | --- |
| Network / 네트워크 | Internet protocols use big-endian (**network byte order**); little-endian hosts must swap header fields / 인터넷은 big-endian, little 호스트는 헤더 필드를 뒤집어야 함 | `htonl` (host → network), `ntohl` |
| Binary files / 바이너리 파일 | A file written on a big-endian machine is misread on a little-endian one / 다른 순서 머신에서 읽으면 숫자가 깨짐 | Format declares the order, reader converts / 포맷이 순서를 명시, 읽는 쪽이 변환 |
| Memory-mapped hardware registers / 하드웨어 레지스터 | Device docs fix a byte layout that may differ from the host / 장치 문서가 정한 배치가 호스트와 다를 수 있음 | Follow the docs / 문서대로 |

**Strings / 문자열 함정** — **EN**: Endianness applies to single multi-byte values only. An ASCII string is a sequence of independent 1-byte values, so the first character is at the lowest address under both conventions. Swapping "everything" fixes integers and corrupts text.
**KO**: endianness는 여러 바이트짜리 값 하나에만 적용돼. ASCII 문자열은 1바이트짜리 독립 값들의 나열이라 어느 방식이든 첫 글자가 가장 낮은 주소에 와. 전부 뒤집으면 정수는 고쳐지고 텍스트는 깨져.

```
"ABCD" (same for big and little / 둘 다 같음)
addr:   0    1    2    3
byte:  'A'  'B'  'C'  'D'
```

---

## 3. Worked example: same 4 bytes, different numbers / 같은 4바이트, 다른 숫자

Bytes `00 00 01 C8` read as a 32-bit unsigned integer. / `00 00 01 C8`을 32비트 unsigned로 읽기.

**big-endian** (offset 0 = MSB):

```
0x00·2^24 + 0x00·2^16 + 0x01·2^8 + 0xC8·2^0 = 0 + 0 + 256 + 200 = 456
```

**little-endian** (offset 0 = LSB, read as `C8 01 00 00`):

```
0xC8·2^24 + 0x01·2^16 + 0x00·2^8 + 0x00 = 3,355,443,200 + 65,536 = 3,355,508,736
```

**EN** — The values differ by a factor of over seven million, and nothing crashes: the wrong number just flows on, which makes these bugs hard to find.
**KO** — 두 값은 700만 배 넘게 차이 나. 더 무서운 건 에러가 안 난다는 거야. 틀린 숫자가 그대로 계산에 흘러가서 디버깅이 힘들어.

```python
data = bytes([0x00, 0x00, 0x01, 0xC8])
int.from_bytes(data, byteorder='big')     # 456
int.from_bytes(data, byteorder='little')  # 3355508736
```

| Tool / 도구 | Default order / 기본값 | Note / 주의 |
| --- | --- | --- |
| `int.from_bytes` | none in the book (argument required); `'big'` default since Python 3.11 / 책은 필수라고 설명, 3.11부터 기본값 `'big'` | be explicit / 명시하자 |
| `struct` | **native** (this machine) / 내 머신 순서 | prefix `>` big, `<` little, `!` network (= big). 6.2's `"!BQ"` is this `!` / 6.2 `"!BQ"`의 `!`가 이거 |

---

## 4. Conversion cost / 변환 비용

**EN** — Reversing byte order is a **byteswap**: ⌊k/2⌋ exchanges for a k-byte value (2 for 32-bit, 4 for 64-bit). CPUs have a dedicated instruction (`BSWAP` on x86-64), so one value is nearly free. For millions of values (e.g. streaming 64-bit floats to a big-endian network) it can be a measurable share of CPU time, so formats like **HDF5** and **Apache Arrow** record the byte order and convert only when the reader differs.

**KO** — 바이트 순서 뒤집기가 **byteswap**이야. k바이트 값이면 교환 ⌊k/2⌋번 (32비트 2번, 64비트 4번). 전용 명령어(x86-64 `BSWAP`)가 있어서 값 하나는 거의 공짜야. 근데 수백만 개면 CPU 시간에서 눈에 띄는 비중이 될 수 있어. 그래서 **HDF5**, **Apache Arrow**는 바이트 순서를 기록만 해두고 읽는 쪽이 다를 때만 변환해.

| Order / 방식 | Advantage / 장점 |
| --- | --- |
| big-endian | memory dumps read like written hex / 메모리 덤프가 사람이 쓰는 순서와 같아서 읽기 편함 |
| little-endian | a value's address is its LSB's address, so narrowing to a smaller type needs no address change / 값의 주소 = LSB의 주소라서 더 작은 타입으로 자를 때 시작 주소를 안 옮겨도 됨 |

Example / 예시: `0x00000005` little-endian at address 100 = `05 00 00 00`; reading 1 or 2 bytes at 100 still gives 5. / 1바이트나 2바이트로 읽어도 5.

---

## 5. Exercises: approach only / 연습문제: 접근법만

1. **`DE AD BE EF` at addresses 100–103: value under big and little?** / **big, little로 읽은 값은?**
   - EN: multiply each byte by 2^24, 2^16, 2^8, 1. The big-endian answer is a famous hex word; check with `hex()`.
   - KO: 각 바이트에 2^24, 2^16, 2^8, 1을 곱해. big 답은 유명한 16진수라 검산하기 쉬워. `hex()`로 확인해.
2. **Two claims: (A) writing a 16-bit int to a file and reading it on the same machine ignores endianness; (B) a plain byte array (0–255) ignores endianness.** / **두 주장 평가**
   - EN: (A) same convention on write and read? (B) is there a multi-byte value to reorder? Boundary case: a uint16 array packed into a byte buffer. Both are correct, but for different reasons; say why.
   - KO: (A) 쓸 때와 읽을 때 같은 규칙인가? (B) 뒤집을 여러 바이트 값이 있나? 경계 케이스: uint16 배열을 바이트 버퍼에 담은 경우. 둘 다 맞지만 근거가 다르다는 걸 써.
3. **`byteswap32(n)` without `struct` or `int.from_bytes`** / **`struct`, `int.from_bytes` 금지**
   - EN: extract bytes with `>>` and `& 0xFF`, reassemble reversed with `<<` and `|`. Test: `0x12345678 → 0x78563412`; applying twice returns the input.
   - KO: `>>`와 `& 0xFF`로 바이트를 꺼내고 `<<`와 `|`로 거꾸로 조립. 테스트: `0x12345678 → 0x78563412`, 두 번 적용하면 원래 값.

```
n = 0x12345678
(n >> 0)  & 0xFF → 0x78   lowest byte / 맨 아래 바이트
(n >> 8)  & 0xFF → 0x56
(n >> 16) & 0xFF → 0x34
(n >> 24) & 0xFF → 0x12   highest byte / 맨 위 바이트
```

Without `& 0xFF` the higher bits come along and mix into the result. / `& 0xFF`를 빼면 위쪽 비트가 따라와서 섞여.

---

## 6. Common confusions / 자주 헷갈리는 것

| Confusion / 헷갈림 | Answer / 정리 |
| --- | --- |
| Little-endian reverses bits too? / 비트도 뒤집혀? | No, only byte order. `0x30` stays `0x30`. / 바이트 순서만 |
| Hex digits reversed? / 니블도 뒤집혀? | No: `12 34 56 78` → `78 56 34 12`, not `87 65 43 21` |
| Does endianness change the value? / 값이 바뀌어? | No, only placement in memory. / 놓는 순서만 |
| Swap strings too? / 문자열도 뒤집어? | No, sequences of 1-byte values (ASCII). / 해당 없음 |
| When should I care? / 언제 신경 써? | Files, network, hardware: bytes crossing a different convention. / 다른 규칙과 바이트를 주고받을 때만 |
| `struct` defaults to big? / 기본값 big? | Native. Use `>`, `<`, `!`. / native야 |
| Address 32/64-bit vs 8-bit cells? / 주소는 32·64비트인데 칸은 8비트? | Addresses are positions, not stored data; a 4-byte int is 4 addresses on any machine. / 주소는 저장되는 값이 아니라 위치. 4바이트 int는 어느 머신이든 주소 4개 |
