# APDR Ch. 6.2 Addressing — Study Notes (EN / KO)

Each section gives the English first, then the Korean. Exercises get the approach only, no finished solutions.
각 섹션은 영어 먼저, 그다음 한국어야. 연습문제는 접근법만 있고 완성된 풀이는 없어.

---

## 0. Big picture / 큰 그림

**EN** — 6.2 answers one question: how are memory cells named (addresses), how many bits do those names need, and how does the naming scheme affect speed? Almost every calculation is `log2` and powers of two.

**KO** — 6.2가 다루는 건 이거야. 메모리 칸에 이름(주소)을 어떻게 붙이고, 그 이름이 몇 비트 필요하고, 그 이름 체계가 속도에 어떤 영향을 주나. 계산 문제는 거의 전부 `log2`랑 2의 거듭제곱으로 풀려.

| Part / 파트 | One line / 한 줄 요약 | Exam point / 시험 포인트 |
| --- | --- | --- |
| Byte addressability | One address = one byte is today's standard / 주소 1개 = 1바이트가 현대 표준 | word vs byte |
| Address space arithmetic | n-bit address → 2^n cells / n비트 주소 → 2^n개 칸 | address-bit counting / 주소 비트 수 계산 |
| Alignment | An n-byte value should start at a multiple of n / n바이트 값은 n의 배수 주소에서 시작해야 빠름 | padding size / 패딩 크기 |
| Memory wall | CPUs got fast, DRAM did not / CPU는 빨라졌는데 DRAM은 안 따라옴 | latency vs bandwidth |
| Module geometry + interleaving | Chips → modules → memory / 칩 → 모듈 → 메모리 | chip count, module count, bit split / 칩 수, 모듈 수, 비트 분할 |

**Units / 단위:** Ki = 2^10, Mi = 2^20, Gi = 2^30. In this chapter 1 GiB is 2^30 bytes, not 10^9. / 이 챕터에서 1 GiB는 10^9가 아니라 2^30바이트야.

---

## 1. Byte addressability / 주소 하나가 가리키는 크기

**EN** — Memory is a long array of cells, each with a number (its address). The key design choice is how big one cell is.

**KO** — 메모리는 길게 늘어선 칸들의 배열이고, 각 칸에 번호(주소)가 붙어 있어. 핵심 설계 선택은 칸 하나를 몇 비트로 할지야.

| Scheme / 방식 | One address names / 주소 1개가 가리키는 것 | Pro / 장점 | Con / 단점 |
| --- | --- | --- | --- |
| word-addressable | one word (e.g. 16 bits on a 16-bit machine) / 워드 1개 | fewer addresses / 주소를 적게 씀 | awkward for single bytes / 1바이트만 읽고 쓰기 불편 |
| byte-addressable | exactly one byte (8 bits) / 정확히 1바이트 | `char` fits one cell, partial updates possible / 1바이트 타입이 칸 하나에 맞고, 부분 수정 가능 | more address bits for the same capacity / 같은 용량에 주소 비트가 더 필요 |

**EN** — Modern systems are byte-addressable, so a 32-bit memory row occupies four consecutive addresses. Partial updates (changing one byte of a 4-byte int) need byte-enable signals on the bus.

**KO** — 현대 시스템은 거의 전부 byte-addressable이야. 그래서 32비트 한 줄이 연속된 주소 4개를 차지해. 4바이트 int 중 1바이트만 바꾸는 부분 수정은 버스에 byte-enable 신호가 있어야 가능해.

```
row 0:  [addr 0][addr 1][addr 2][addr 3]   ← one 32-bit row / 32비트 한 줄
row 1:  [addr 4][addr 5][addr 6][addr 7]
```

---

## 2. Address space arithmetic / 주소 비트 수 계산

**EN** — n address bits name 2^n units; N units need log2 N bits. "Unit" means bytes if byte-addressable, words if word-addressable.

**KO** — n비트 주소로는 2^n개 칸을 부를 수 있고, 칸이 N개면 log2 N비트가 필요해. "칸"은 byte-addressable이면 바이트, word-addressable이면 워드야.

```
address bits = log2(number of addressable units)
```

- 32-bit: 2^32 bytes = 4 GiB. That is why 32-bit OSes could not use more than 4 GiB of RAM (PAE was a workaround). / 32비트 OS가 4 GiB 넘게 못 쓰던 이유 (PAE로 우회).
- 64-bit: 2^64 bytes ≈ 1.8 × 10^10 GiB, far beyond any real machine. / 물리적으로 다 채울 일 없음.

### word vs byte: how many extra bits? / 비트가 몇 개 차이 나나

Example: **4 GiB × 32 bit** = 4 Gi rows, each 32 bits wide. (4 GiB is the row count here, not the byte count.)
예제: **4 GiB × 32 bit** = 32비트짜리 줄이 4 Gi개라는 뜻이야. (4 GiB는 전체 바이트 수가 아니라 줄 개수.)

| Scheme / 방식 | Units named / 부르는 칸 수 | Bits / 비트 |
| --- | --- | --- |
| word-addressable | 4 Gi = 2^32 rows | 32 |
| byte-addressable | 4 Gi × 4 bytes = 2^34 bytes | 34 |

**EN** — In general, byte addressing needs **log2(W/8) extra bits** for row width W. Total storage (bits) does not change; only the naming does.

**KO** — 일반화하면 줄 폭이 W비트일 때 byte addressing은 **log2(W/8)비트를 더** 요구해. 저장 용량(비트 총량)은 안 변하고, 이름 붙이는 방식만 바뀌는 거야.

---

## 3. Alignment & padding / 왜 구조체가 부풀어 있나

**EN** — A value is **aligned** if its start address is a multiple of its size (4-byte int → multiple of 4, 8-byte double → multiple of 8). Controllers and caches fetch aligned blocks in one transaction; an unaligned value that straddles a boundary needs two, roughly doubling latency. Some architectures raise an exception instead. Compilers insert **padding** automatically.

**KO** — 값의 시작 주소가 자기 크기의 배수면 **aligned**야 (4바이트 int는 4의 배수, 8바이트 double은 8의 배수). 컨트롤러랑 캐시는 정렬된 블록을 한 번에 가져와서, 경계에 걸친 비정렬 값은 트랜잭션이 2번 필요해(지연 약 2배). 어떤 아키텍처는 아예 exception을 내. 그래서 컴파일러가 알아서 **padding**을 끼워 넣어.

```
addr:      0  1  2  3 | 4  5  6  7
aligned:  [ int @0    ]               ← one block / 블록 1개
unaligned:      [ int @2   ]          ← crosses 3|4 → two blocks / 경계 걸침 → 블록 2개
```

```python
import struct
struct.calcsize("!BQ")   # 9   '!' = network (big-endian), no padding / 패딩 없음
struct.calcsize("@BQ")   # 16  '@' = native, aligned + padded / 정렬 + 패딩
```

```
'!BQ':  [B][Q Q Q Q Q Q Q Q]            = 1 + 8     = 9
'@BQ':  [B][pad×7][Q Q Q Q Q Q Q Q]     = 1 + 7 + 8 = 16
         0   1..7   8 ← Q starts at a multiple of 8 / Q가 8의 배수에서 시작
```

**EN** — Padding rule: round the next field's offset up to a multiple of its size. Structs also round their total size up to a multiple of their largest member (tail padding), so field order matters: `{char, double, char}` = 24 bytes, `{double, char, char}` = 16 bytes. A 1-byte value (e.g. an ASCII char) is always aligned.

**KO** — 패딩 계산법: 다음 필드의 시작 위치를 그 필드 크기의 다음 배수로 올림해. 구조체는 전체 크기도 가장 큰 멤버의 배수로 맞춰서(끝 패딩) 필드 순서에 따라 크기가 달라져. `{char, double, char}` = 24바이트, `{double, char, char}` = 16바이트야. 1바이트 값(ASCII 문자 등)은 어디 있어도 항상 정렬된 거야.

---

## 4. Memory wall / CPU는 달리는데 메모리는 걷는다

**EN** — From the 1980s to the 2000s CPU performance roughly doubled every two years while DRAM latency improved slowly (capacitor charge/sense time and refresh do not shrink like transistor switching). The gap is the **memory wall** (term from the mid-1990s). A 3 GHz CPU can do ~10^10 simple ops/s; one DRAM miss (tens to 100+ ns) costs hundreds of instructions. Caches exist to hide this.

**KO** — 1980~2000년대 CPU 성능은 대략 2년마다 2배씩 늘었는데, DRAM 레이턴시는 훨씬 느리게 줄었어(커패시터 충전·감지 시간과 refresh가 트랜지스터처럼 빨리 안 줄어). 이 격차가 **memory wall**이야. 3 GHz CPU는 초당 약 10^10개 연산을 하는데, DRAM까지 가는 miss 한 번(수십~100ns 이상)이면 명령 수백 개를 처리할 시간이 날아가. 캐시는 이걸 숨기려고 있는 거야.

| | latency | bandwidth |
| --- | --- | --- |
| Meaning / 뜻 | time for one request to return / 요청 하나가 돌아오는 시간 | data per unit time / 단위 시간당 옮기는 양 |
| Analogy / 비유 | highway length / 고속도로 길이 | number of lanes / 차선 수 |
| Hidden by / 숨기는 방법 | prefetch, caches | cannot be hidden: bus width × clock is a hard ceiling / 못 숨김. 물리적 천장 |

**EN** — Streaming algorithms hit the bandwidth ceiling before running out of arithmetic: they are **memory-bound**, and are analyzed by **arithmetic intensity** = FLOPs / bytes transferred from memory.

**KO** — 큰 배열을 쓸고 지나가는 알고리즘은 연산 능력이 남는데도 bandwidth 천장에 먼저 부딪혀. 이게 **memory-bound**고, 이런 알고리즘은 **arithmetic intensity** = 연산(FLOP) 수 / 메모리에서 옮긴 바이트 수로 분석해.

---

## 5. Chips → modules → memory, and interleaving / 칩 → 모듈 → 메모리, 그리고 interleaving

**EN** — A **memory module** (SO-DIMM for laptops, DIMM for desktops) is a PCB carrying several **DRAM packages** (chips). An address names a location in the logical address space, not a chip; several chips can each supply some bits of the same word.

**KO** — **memory module**(노트북은 SO-DIMM, 데스크탑은 DIMM)은 **DRAM 칩** 여러 개를 얹은 기판이야. 주소는 칩 하나가 아니라 논리적 주소 공간의 위치를 가리키고, 여러 칩이 같은 워드의 비트를 나눠서 내.

### Worked example: 1 GiB × 32 bit from 256 Mi × 4 bit chips (word-addressable)

| Step / 단계 | EN | KO |
| --- | --- | --- |
| 1. Chips per module | 32 / 4 = **8 chips in parallel** → one 32-bit word | 폭 맞추기: 8개를 나란히 |
| 2. Modules | 2^30 / 2^28 = **4 modules** | 깊이 맞추기: 4개 |
| 3. Total chips | 8 × 4 = **32** | 총 32개 |
| 4. Address bits | 30 = 2 (module select) + 28 (row within module) | 30비트 = 모듈 2 + 줄 28 |

**EN** — Width is matched side by side (no extra address bits); depth is matched by stacking (adds module-select bits). Switching this memory to byte addressing: 30 → **32** bits, same capacity.

**KO** — 폭(비트 수)은 옆으로 나란히 붙여서, 깊이(줄 수)는 위아래로 쌓아서 맞춰. 옆으로 붙이는 건 주소 비트를 안 늘리고, 쌓는 것만 모듈 선택 비트를 늘려. 이 메모리를 byte addressing으로 바꾸면 30 → **32**비트, 용량은 그대로.

### High-order vs low-order interleaving

**EN** — The `interleave` choice is which end of the address the module bits are taken from.

**KO** — `interleave`는 모듈 번호를 주소의 어느 쪽 비트에서 떼어내느냐야.

| | high-order | low-order |
| --- | --- | --- |
| Module bits / 모듈 비트 | top 2 (bit 29–28) / 맨 위 2비트 | bottom 2 (bit 1–0) / 맨 아래 2비트 |
| Row / 줄 번호 | lower 28 bits / 아래 28비트 | upper 28 bits / 위 28비트 |
| Address 14 | module 0, row 14 | module 2, row 3 |
| Consecutive addresses / 연속 주소 | fill module 0, then module 1 / 모듈 0을 다 채우고 다음으로 | cycle 0,1,2,3,0,… / 돌아가며 분산 |
| Good for / 잘하는 것 | independent units on separate modules / 서로 다른 장치가 독립 접근 | 4 consecutive words fetched **in parallel** → max sequential bandwidth / 순차 접근 bandwidth 최대 |

Small picture with 4 modules and 16 addresses / 모듈 4개, 주소 16개로 보면:

```
high:  m0 = [0 1 2 3]   m1 = [4 5 6 7]   m2 = [8 9 10 11]  m3 = [12 13 14 15]
low:   m0 = [0 4 8 12]  m1 = [1 5 9 13]  m2 = [2 6 10 14]  m3 = [3 7 11 15]
```

Bit-level / 비트 연산으로:

```python
addr = 14                             # 0b1110
# low-order (4 modules = bottom 2 bits)
module = addr & 0b11                  # 2
row    = addr >> 2                    # 3
# high-order (30-bit address, top 2 bits)
module = addr >> 28                   # 0
row    = addr & ((1 << 28) - 1)       # 14
```

**EN** — High-order needs the **full address width** (30 bits). 14 fits in 4 bits, but in the 30-bit view its top two bits are 00.

**KO** — high-order는 **전체 주소 폭(30비트)**을 알아야 계산돼. 14는 4비트로 표현되지만 30비트 기준으로 보면 위 2비트가 00이야.

---

## 6. Exercises: approach only / 연습문제: 접근법만

1. **36-bit bus, byte-addressable → max GiB? Same memory, 8-byte words → how many bits?**
   - EN: split 2^36 into 2^30 × 2^?. Going from 1-byte to 8-byte units divides the count by 8 = 2^3.
   - KO: 2^36을 2^30 × 2^?로 쪼개. 칸 단위가 1바이트 → 8바이트면 칸 수가 1/8(= 2^3)이 돼.
2. **"Byte addressing always needs more bits and never changes capacity." Evaluate.**
   - EN: try a 1-byte word (identical schemes). Non-power-of-two words (3 bytes) need a ceiling, not exactly log2 w. For "capacity", ask what is held fixed: physical memory fixed → capacity unchanged; address width fixed → addressable capacity shrinks. Implicit assumptions: one address = one unit, no address space reserved for memory-mapped I/O.
   - KO: 워드가 1바이트면 두 방식이 같아. 워드가 2의 거듭제곱이 아니면(3바이트) 올림이 필요해서 딱 log2 w가 아니야. "용량"은 뭘 고정했는지 따져: 물리 메모리 고정이면 그대로, 주소 폭 고정이면 접근 가능 용량이 줄어. 숨은 가정: 주소 하나 = 단위 하나, memory-mapped I/O로 떼어준 주소 공간 없음.
3. **`module_and_row(word_address, num_modules, interleave)`**
   - EN: module bits `k = num_modules.bit_length() - 1`. low: mask with `num_modules - 1`, shift right by k. high: needs total width (30 here; consider an `addr_bits=30` default parameter). String route: `f"{addr:030b}"` (note the `0`), slice `[:k]` / `[k:]` (high) or `[-k:]` / `[:-k]` (low). Expected: `(14, 4, 'low') → (2, 3)`, `(14, 4, 'high') → (0, 14)`.
   - KO: 모듈 비트 수 `k = num_modules.bit_length() - 1`. low는 `num_modules - 1`로 마스킹하고 k칸 오른쪽 시프트. high는 전체 폭이 필요해(여기선 30, `addr_bits=30` 기본값 인자 추천). 문자열로 풀면 `f"{addr:030b}"`(0 빼먹지 말 것)로 만들고 high는 `[:k]`/`[k:]`, low는 `[-k:]`/`[:-k]`로 잘라.

---

## 7. Common confusions / 자주 헷갈리는 것

| Confusion / 헷갈림 | Answer / 정리 |
| --- | --- |
| 32-bit address × 32-bit cell = 16 GiB? / 32비트 주소면 32 × 4G? | Address width ≠ cell size. Byte-addressable: 2^32 names × 1 byte = 4 GiB. Only word-addressable with 4-byte words gives 16 GiB. / 주소 폭과 칸 크기는 별개. byte-addressable이면 2^32 × 1바이트 = 4 GiB |
| Who generates addresses? / 주소는 누가 만드나 | The CPU computes them (base + index × size + offset), the MMU translates virtual → physical, caches are checked, and on a miss the memory controller splits the bits into channel/bank/row/column. The OS manages the space. / CPU가 계산, MMU가 번역, 캐시 확인, miss면 메모리 컨트롤러가 비트를 쪼개 DRAM에 전송. OS는 공간 관리 |
| 64-bit CPU + 32-bit OS? | Still 4 GiB per program: the OS uses 32-bit pointers. / 그래도 4 GiB. OS 포인터가 32비트라서 |
| "4 GiB × 32 bit" = total bytes? | No: 4 Gi **rows** of 32 bits = 16 GiB total. / 줄 개수가 4 Gi, 총량은 16 GiB |
| GiB = 10^9? | 2^30 in this chapter. / 이 챕터에서는 2^30 |
| Byte addressing adds memory? / 메모리가 늘어나나 | No, only finer names. / 이름만 잘게 쪼갤 뿐 |
| Side-by-side chips add address bits? / 칩을 옆으로 붙이면 비트 증가? | No. Only stacking (more modules) does. / 아니. 쌓을 때만 늘어 |
| Address 14's top bits under high-order = 11? | Only if you look at 4 bits. In 30 bits they are 00. / 30비트 기준이면 00 |
| Unaligned → wrong value? / 비정렬이면 틀린 값? | Usually just slower (two transactions); some architectures fault. / 보통은 느려질 뿐, 일부만 exception |
