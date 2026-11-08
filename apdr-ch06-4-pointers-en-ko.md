# APDR Ch. 6.4 Pointers, Object Lifetimes and Ownership — Study Notes (EN / KO)

Each section gives the English first, then the Korean. Exercises get the approach only, no finished solutions.
각 섹션은 영어 먼저, 그다음 한국어야. 연습문제는 접근법만 있고 완성된 풀이는 없어.

---

## 0. Big picture / 큰 그림

**EN** — A pointer is a variable whose value is an address. 6.4 asks: what does carrying addresses around buy you, and who is responsible for the object behind the address dying at the right time? On a 64-bit machine a pointer is 8 bytes; this is the one case where an address really is stored as data.

**KO** — pointer는 주소를 값으로 저장하는 변수야. 6.4의 질문은 이거야. 주소를 들고 다니면 무슨 힘이 생기고, 그 주소가 가리키는 객체가 언제 죽는지 누가 책임지나. 64비트 머신에서 포인터는 8바이트야. 주소가 진짜로 데이터로 저장되는 유일한 경우지.

```
addr 1000:  [ x = 42 ]       ← int x (4 bytes)
addr 2000:  [ p = 1000 ]     ← int *p, holds x's address (8 bytes)
            *p → go to 1000 → 42
```

| Part / 파트 | One line / 한 줄 요약 | Exam point / 시험 포인트 |
| --- | --- | --- |
| `&`, `*`, arithmetic | `p + k` moves k elements, not k bytes / k바이트가 아니라 k개 원소 | address calculation / 주소 계산 |
| Stack / heap / static | three object lifetimes / 수명 3종류 | dangling vs leak |
| Worked example | pointer difference = element count / 포인터 뺄셈 = 원소 개수 | bytes vs elements |
| Python | variables are name tags, not boxes / 변수는 상자가 아니라 이름표 | aliasing, shallow copy |
| C++ RAII | released automatically at scope exit / 스코프 끝나면 자동 정리 | ownership |

---

## 1. Address-of, dereference, pointer arithmetic

| Operator / 연산자 | Name | Meaning / 뜻 |
| --- | --- | --- |
| `&x` | address-of | give me the address of x / x의 주소 |
| `*p` | dereference | go to the address in p and read/write there / p에 든 주소로 가서 읽고 쓰기 |

```c
int x = 42;
int *p = &x;   // p holds x's address / p에 x의 주소
int y = *p;    // read through p → 42
*p = 99;       // write through p → x == 99
```

**EN** — The `*` in `int *p` is part of the declaration ("p points to int"); the `*` in `*p = 99` is the dereference operator. Same symbol, different roles.
**KO** — `int *p`의 `*`는 선언(p는 int를 가리키는 포인터)이고, `*p = 99`의 `*`는 역참조 연산이야. 기호는 같은데 역할이 달라.

**Rule / 핵심 규칙** — **EN**: the pointer type sets how many bytes are read and how they are interpreted, and the step size: adding k to a `T*` advances k × sizeof(T) bytes. **KO**: 포인터 타입은 몇 바이트를 어떻게 해석할지와 연산의 보폭을 정해. `T*`에 k를 더하면 k × sizeof(T) 바이트 이동해.

```
int arr[5];   // sizeof(int) = 4, starts at 1000
pointer:  arr    arr+1  arr+2  arr+3  arr+4
address:  1000   1004   1008   1012   1016
```

`arr[i]` is shorthand for `*(arr + i)`. In machine code this is `[base + index*4]`. / `arr[i]`는 `*(arr + i)`의 줄임말이고, 기계어로는 `[base + index*4]`야.

### Undefined behaviour (UB)

**EN** — Pointer arithmetic is defined only within one array, plus one past the end (may be compared, not dereferenced). Anything else is UB: the standard promises nothing, the compiler assumes it never happens, and the program may look fine in tests and break later.

**KO** — 포인터 연산은 배열 하나 안에서만 정의돼. 끝 바로 다음 칸까지는 가리키고 비교만 OK, 역참조는 안 돼. 나머지는 UB야. 표준이 아무것도 보장 안 하고, 컴파일러는 UB가 절대 안 일어난다고 가정해. 그래서 테스트에선 멀쩡하다가 나중에 터져.

```
int arr[5];
arr + 5   → point/compare OK, *(arr + 5) is UB
arr + 6   → UB just to form it / 만드는 것만으로 UB
arr - 1   → UB
```

### Double pointers `int **`

**EN** — C passes every argument by value, so to let a function change the caller's pointer you pass the pointer's address. This is the standard "allocate inside a function, return through a parameter" idiom.
**KO** — C는 인자를 전부 값으로 복사해서 넘기니까, 함수가 호출한 쪽의 포인터 자체를 바꾸려면 포인터의 주소를 넘겨야 해. 함수 안에서 할당하고 인자로 돌려주는 표준 패턴이야.

```c
void alloc_int(int **pp) { *pp = malloc(sizeof(int)); }
int *p = NULL;
alloc_int(&p);   // now p points to heap memory
```

---

## 2. Stack, heap, static: object lifetimes / 객체의 수명

| Kind / 종류 | Created by / 만드는 법 | Born / 태어남 | Dies / 죽음 | Lives in / 사는 곳 | Alloc cost / 할당 비용 |
| --- | --- | --- | --- | --- | --- |
| automatic | local variable / 함수 안 일반 변수 | block entry | block exit | **stack** | ~free (move stack pointer) |
| static | file scope or `static` | program start | program end | fixed segment | none (fixed at link) |
| dynamic | `malloc` (`new` in C++) | malloc call | **`free`** | **heap** | variable (search free lists, ask OS) |

```
high addr  [ stack  ]  ↓ grows per call, shrinks on return (LIFO)
           [  ...   ]
           [ heap   ]  ↑ malloc on demand
           [ static ]
low addr   [ code   ]
```

**EN** — The stack is a pile of plates: each call pushes a **stack frame**, return pops it whole. Fast, but everything on that plate disappears.
**KO** — stack은 접시 쌓기야. 함수 호출마다 **stack frame**을 올리고 리턴하면 통째로 치워. 빠르지만 그 접시 위의 건 같이 사라져.

### Bug 1: dangling pointer

```c
int *bad_return(void) {
    int local = 7;
    return &local;   // local dies with the frame / 리턴하는 순간 사라짐
}
```

**EN** — The returned address looks valid but the slot belongs to nobody; the next call overwrites it. It may pass tests and fail later; the compiler need not warn.
**KO** — 돌려받은 주소는 멀쩡해 보이지만 그 자리는 이미 주인이 없고, 다음 호출이 덮어써. 테스트에선 돌다가 나중에 터지고, 컴파일러가 잡아줄 의무도 없어.

### Bug 2: memory leak

```c
void leak(void) {
    int *p = malloc(100 * sizeof(int));
    // return without free(p): p (stack) vanishes, 400 heap bytes stay ownerless
}
```

| | dangling pointer | memory leak |
| --- | --- | --- |
| What / 무슨 일 | pointer alive, object dead / 포인터는 살아 있는데 객체가 죽음 | object alive, pointer lost / 객체는 살아 있는데 포인터를 잃음 |
| Where / 주로 | stack (returning a local's address), use after `free` | heap |
| Effect / 결과 | garbage, crashes (UB) | memory piles up |

**Rule / 규칙**: exactly one `free` per `malloc`, on every execution path, error paths included. / malloc 한 번에 free 정확히 한 번, 에러로 일찍 빠지는 경로까지 모든 경로에서.

---

## 3. Worked example: pointer difference counts elements / 포인터 뺄셈은 원소 개수

```c
double arr[5] = {1.1, 2.2, 3.3, 4.4, 5.5};   // sizeof(double) = 8, base 1000
double *p = arr;        // 1000
double *q = arr + 4;    // 1032
ptrdiff_t diff = q - p; // 4
```

**EN** — The byte distance is 32 but `q - p` is 4: addition is scaled by sizeof, subtraction divides by it. For bytes, cast both to `char*` first: `(char*)q - (char*)p == 32`. Mixing these up in byte-oriented code (networking, serialization, 6.3) gives offsets off by a factor of 8.

**KO** — 바이트 차이는 32인데 `q - p`는 4야. 더하기는 sizeof로 곱해지고 빼기는 sizeof로 나눠져. 바이트 거리가 필요하면 둘 다 `char*`로 캐스트한 뒤 빼: `(char*)q - (char*)p == 32`. 네트워크·직렬화(6.3)처럼 바이트로 일하는 코드에서 헷갈리면 오프셋이 8배씩 틀려.

---

## 4. Python: variables are name tags / 변수는 이름표

**EN** — A C variable is a box holding a value; a Python variable is a name bound to an object. Python has no `&` or `*`, but every name behaves like a pointer.
**KO** — C 변수는 값이 든 상자, Python 변수는 객체에 붙인 이름표야. 파이썬엔 `&`나 `*`가 없지만 모든 이름이 포인터처럼 동작해.

```python
a = [10, 20, 30]
b = a          # same object, second name / 같은 객체에 이름표 하나 더
b[0] = 99
print(a)       # [99, 20, 30]
print(a is b)  # True
```

**Aliasing** — **EN**: one object, several names. A design choice (passing a big list is free), with the risk that a function mutating its argument changes the caller's object. **KO**: 한 객체에 이름 여러 개. 설계상 선택이야(큰 리스트를 넘겨도 복사 없음). 대신 함수 안에서 인자를 수정하면 호출한 쪽 객체도 바뀌어.

```python
def add_one(lst): lst.append(1)   # mutate: caller sees it / 호출한 쪽도 바뀜
def rebind(lst):  lst = [1]       # rebind: only the local name moves / 지역 이름만 이동
```

### Three levels of copying / 복사 3단계

| How / 방법 | Copies / 복사 대상 | Inner lists / 안쪽 리스트 |
| --- | --- | --- |
| `b = a` | nothing (same object) / 없음 | shared / 공유 |
| `a.copy()`, `a[:]`, `list(a)` | **shallow**: outer list only / 바깥만 | **still shared** / 여전히 공유 |
| `copy.deepcopy(a)` | **deep**: recursively / 재귀적으로 | independent / 독립 |

```python
original = [[1, 2], [3, 4]]
shallow = original[:]
shallow[0][0] = 99
print(original)   # [[99, 2], [3, 4]]
```

**EN** — Immutable objects (int, str, tuple of immutables) can be shared safely: nothing can change them. Rule for an independent copy: every reachable mutable object must be new; immutable leaves may be shared. Even `copy.deepcopy` returns the same int objects. Careful: a tuple holding lists is not safe to share.

**KO** — 불변 객체(int, str, 불변만 든 tuple)는 공유해도 안전해. 아무도 못 고치니까. 독립 복사의 규칙: 도달 가능한 모든 가변 객체는 새로 만들고, 불변 잎사귀는 공유해도 돼. `copy.deepcopy`도 int는 같은 객체를 돌려줘. 주의: 리스트가 든 튜플은 공유하면 안전하지 않아.

### `id()` and memory reclamation / 메모리 회수

- `id(obj)`: unique per object; in CPython 3.13 it is the address (implementation detail). / CPython에선 실제 주소지만 구현 디테일
- `is` = same object; `==` = equal value. / `is`는 같은 객체, `==`는 같은 값
- **Reference counting**: most objects live on the heap and count their names; at zero they are usually freed promptly. / 이름표 수가 0이면 보통 바로 회수
- **Cyclic GC**: cycles (A → B → A) never reach zero, so a separate collector finds them. / 순환 참조는 별도 수거기
- **EN**: no dangling pointers in Python; the hazard is aliasing. **KO**: 파이썬엔 dangling이 없어. 조심할 건 aliasing.

---

## 5. Ownership and RAII (C++)

**EN** — In C, someone must own each heap object, i.e. be responsible for `free`, along every path. Miss one → leak; free twice → UB. **RAII** (Resource Acquisition Is Initialization) ties a resource to an object's lifetime: the constructor acquires, the destructor releases, and destructors run automatically at scope exit, even through exceptions. Python's `with open(...)` follows the same idea.

**KO** — C에서는 힙 객체마다 누가 free할 책임(ownership)이 있는지 사람이 추적해야 해. 하나 빠지면 leak, 두 번 하면 UB. **RAII**는 자원을 객체의 수명에 묶어. 생성자가 획득, 소멸자가 해제, 스코프를 벗어나면 예외가 나도 소멸자가 자동으로 불려. 파이썬의 `with open(...)`도 같은 발상이야.

| | `std::unique_ptr` | `std::shared_ptr` |
| --- | --- | --- |
| Ownership / 소유 | sole / 단독 | shared / 공유 |
| Copy / 복사 | no (copy ctor deleted), move only / 이동만 | yes |
| Freed when / 해제 | owner leaves scope / 주인이 스코프를 벗어날 때 | refcount hits 0 / 카운트 0 |
| Analogy / 비유 | one house key / 열쇠 하나 | flatmates, last one out turns off the lights / 마지막 사람이 불 끔 |

| | C | C++ (RAII) | Python |
| --- | --- | --- | --- |
| Who frees / 해제 담당 | programmer (`free`) | destructor (scope) | interpreter (refcount + GC) |
| When / 시점 | you decide / 직접 | scope end, predictable / 예측 가능 | usually promptly, **not guaranteed** / 보장 안 됨 |
| Main risk / 주요 위험 | leak, dangling, double free | cyclic `shared_ptr` | aliasing |

**EN** — `del x` removes one name; the object survives if other names remain.
**KO** — `del x`는 이름표 하나를 떼는 거야. 다른 이름표가 남아 있으면 객체는 살아 있어.

---

## 6. C vs Python behaviour side by side / C와 Python 행동 비교

**EN** — The mechanisms differ, but there are always two questions: mutate the target, or rebind where it points?
**KO** — 메커니즘은 달라도 질문은 두 개야. 가리키는 대상을 고치나(mutate), 가리키는 곳을 바꾸나(rebind).

| | C | Python |
| --- | --- | --- |
| Variable / 변수 | box with a value / 값이 든 상자 | name tag on an object / 이름표 |
| `x = x + 1` | overwrite the same box (same address) / 같은 상자 덮어쓰기 | get a new int, move the tag (`id` changes) / 새 int, 이름표 이동 |
| Value copy | `int b = a;` | none; sharing immutables has the same effect / 불변 공유가 같은 효과 |
| Mutate target / 대상 수정 | `*p = 99` | `a[0] = 99` |
| Rebind / 가리키는 곳 변경 | `p = &y` | `a = [7]` |
| Visible to the other name? / 다른 쪽에 보이나 | only mutation / 수정만 | only mutation / 수정만 |

```
Python immutable shared (int, str, tuple)  ≈  C value copy       → looks independent / 따로 노는 것처럼
Python mutable shared (list, dict)         ≈  C shared pointer   → changes are seen / 같이 바뀜
```

`+=` trap / 함정:

```python
t = (1, 2); u = t; t += (3,)   # u == (1, 2)      immutable: new object, tag moves
l = [1, 2]; m = l; l += [3]    # m == [1, 2, 3]   mutable: in-place (extend)
```

**When does C need pointers? / C에서 포인터가 필요한 때** — **EN**: most variables are used by name; the compiler turns names into addresses (`[rsp + 12]` for locals, fixed addresses for globals). Pointers are needed only to reach what a name cannot: heap objects (the `malloc` result is the only handle), a caller's variable, large data without copying, arrays and strings, linked structures. **KO**: 대부분은 이름으로 쓰고 주소는 컴파일러가 관리해. 포인터는 이름이 닿지 않는 곳에만 필요해: 힙 객체(`malloc` 결과가 유일한 손잡이), 호출한 쪽 변수, 복사 없는 큰 데이터 전달, 배열·문자열, linked 구조.

**Comparing addresses / 주소로 비교하기**

| What / 무엇 | How / 방법 |
| --- | --- |
| Python object | `a is b`, `hex(id(a))` (the `0x7f...` in tracebacks / 트레이스백의 `0x7f...`) |
| torch tensor buffer | `t.data_ptr()` (a view may have `is` False but share the buffer / view는 `is`가 False여도 버퍼 공유 가능) |
| numpy buffer | `np.shares_memory(a, b)` |

Seeing `<function f at 0x...>` where a number was expected usually means a missing call: `f` vs `f()`, `x.mean` vs `x.mean()`, or an unconsumed generator. / 숫자 자리에 이게 뜨면 보통 호출을 빼먹은 거야.

---

## 7. Triton: sharing one big matrix without copying / 트리톤: 큰 행렬을 복사 없이 나눠 쓰기

**EN** — Thousands of GPU programs (pids) share one large buffer, and each uses pointer arithmetic to pick out its own region. The pointer says "this is your column block, starting here"; nothing is extracted or copied. Copying tiles would be extra memory traffic, and these kernels are mostly memory-bound (6.2).

**KO** — GPU 프로그램(pid) 수천 개가 큰 버퍼 하나를 공유하고, 각자 포인터 연산으로 자기 구역만 골라. 포인터가 "너는 여기서부터 이만큼이 네 열이야"라고 가리키는 거지, 열을 뽑아서 복사해 주는 게 아니야. 타일을 복사하면 그 자체가 메모리 왕복이고, 이런 커널은 대부분 memory-bound(6.2)야.

```
one buffer (HBM)
[ ─── pid 0 ─── | ─── pid 1 ─── | ─── pid 2 ─── ]
  base+0×BLOCK    base+1×BLOCK    base+2×BLOCK
```

matmul C = A × B: each pid reads a row block of A and a column block of B (shared, read-only, by many pids) and writes only its own C tile. / 각 pid가 A의 행 블록과 B의 열 블록을 읽고(여러 pid가 공유) 자기 C 타일만 써.

```python
a_ptrs = a_ptr + offs_m[:, None] * stride_am + offs_k[None, :] * stride_ak
b_ptrs = b_ptr + offs_k[:, None] * stride_bk + offs_n[None, :] * stride_bn
```

- **EN**: B is row-major, so a column block needs strided access (the `column_sum` problem from 6.1); Triton loads whole tiles instead of single columns. Triton pointers are typed like C: +1 on an fp32 pointer moves 4 bytes.
- **KO**: B는 row-major라 열 블록은 stride로 띄엄띄엄 읽어야 해(6.1 `column_sum` 문제). 그래서 열 하나가 아니라 타일 단위로 읽어. 트리톤 포인터도 C처럼 타입이 있어서 fp32 포인터에 +1 하면 4바이트 이동.

| Situation / 상황 | Method / 방법 |
| --- | --- |
| Output regions do not overlap (usual matmul, softmax) / 출력 구역 안 겹침 | each pid `tl.store`s; nothing to merge / 각자 store, 합칠 필요 없음 |
| Several pids add into the same cell (split-K) / 같은 칸에 더함 | `tl.atomic_add`, or partial-sum buffer + second kernel (links to 6.5 coherence) |

**EN** — "Just give pid and size" works only for contiguous 1D element-wise ops, which torch already does. Triton exists for when you must control where and how much to load: row strides, transposed or sliced tensors, 2D tiles, masks. `tl.make_block_ptr` packages shape, strides, offsets and block size, but does the same address math inside.

**KO** — "pid랑 size만 주면 돌게"는 연속된 1D 원소별 연산에서만 되고, 그건 torch로 충분해. 트리톤은 어디서 얼마나 가져올지 직접 정해야 할 때 쓰는 거야: 행 stride, transpose·slice된 텐서, 2D 타일, mask. `tl.make_block_ptr`는 shape, strides, 시작 위치, 블록 크기를 받아 포장해 주지만 안에서 하는 주소 계산은 같아.

---

## 8. Exercises: approach only / 연습문제: 접근법만

1. **`short arr[6]` at address 200, `short *p = arr + 2`: (a) p (b) p + 3 (c) p − arr and its unit (d) p + 3 if `char *p = (char*)arr + 2`**
   - EN: sizeof(short) = 2; multiply when adding, divide when subtracting. Check (b) stays inside the array. In (d) the step is 1; say which byte of which short it hits (links to 6.3).
   - KO: 더할 땐 ×2, 뺄 땐 ÷2. (b)는 배열 범위 안인지 확인. (d)는 보폭이 1이고, 어느 short의 어느 바이트인지 말하면 6.3이랑 엮여.
2. **Why `make_seven` (returns `&n` of a local) is UB, two visible failure modes, and a fixed version**
   - EN: start from the local's storage duration. Failures: the next call overwrites the slot, or a sanitizer aborts. Fix: allocate on the heap, document who frees it, handle `malloc` returning NULL.
   - KO: 지역 변수의 storage duration부터. 고장: 다음 호출이 덮어씀, 또는 sanitizer가 감지해서 종료. 고치기: 힙으로 옮기고 누가 free하는지 적고, NULL 처리.
3. **`deep_independent(lst)` for a list of int lists, without `copy`**
   - EN: new outer list and new inner lists; ints can be shared. Copy once, store the result, then mutate and compare. Show a shallow copy failing the same test. Check `result[0] is original[0]` is False; `result[0][0] is original[0][0]` being True is fine. Trap: `[[]] * n` is one list referenced n times.
   - KO: 바깥도 안쪽도 새로, int는 공유해도 돼. 복사는 한 번만 해서 변수에 담고, 그다음 변경하고 비교해. shallow가 같은 테스트에서 실패하는 것도 보여줘. `result[0] is original[0]`이 False여야 하고, `result[0][0] is original[0][0]`이 True인 건 정상. 함정: `[[]] * n`은 리스트 하나를 n번 가리킴.

---

## 9. Common confusions / 자주 헷갈리는 것

| Confusion / 헷갈림 | Answer / 정리 |
| --- | --- |
| `p + 1` = address + 1? | + sizeof(T): `int*` +4, `double*` +8 |
| `q - p` = byte difference? / 바이트 차이? | element count; cast to `char*` for bytes / 원소 개수 |
| `*` in a declaration vs a dereference | `int *p` declares; `*p = 3` writes through p / 선언 vs 역참조 |
| UB means a crash? / UB면 크래시? | maybe not, which is worse / 안 날 수도 있어서 더 무서움 |
| dangling vs leak | dangling: only the pointer remains; leak: only the object remains / 포인터만 남음 vs 객체만 남음 |
| `b = a` copies in Python? / 복사? | no, another tag on the same object / 이름표 하나 더 |
| `a[:]` is a full copy? / 완전 복사? | shallow: inner lists shared / 안쪽 공유 |
| `del x` frees memory? / 메모리 해제? | removes one tag only / 이름표만 뗌 |
| `id()` is an address? / 주소? | only in CPython, not a language guarantee / CPython에서만 |
| `is` vs `==` | same object vs equal value / 같은 객체 vs 같은 값 |
| Immutable = the C model? / 불변이 C 모델? | no: immutable sharing *behaves like* C value copy, mutable sharing like C pointer sharing / 겉보기 동작만 대응 |
| `void` / `main`? | `void` = "nothing" (no return value, no params, `void*` = untyped address from `malloc`); `main` = program entry point, `return 0` = success exit code / 빈칸 표시, 출입구 이름 |
