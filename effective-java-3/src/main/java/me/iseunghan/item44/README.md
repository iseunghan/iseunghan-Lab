### 함수형 인터페이스 대표적인 6개 소개

---

| 인터페이스               | 함수 시그니처               | 예시                   | 특징             |
|---------------------|-----------------------|----------------------|----------------|
| `UnaryOperator<T>`  | `T apply(T t)`        | `String::toLowerCase` | 인수=반환, 인수 1개   |
| `BinaryOperator<T>` | `T apply(T t1, T t2)` | `BigInteger::add`    | 인수=반환, 인수 2개   |
| `Predicate<T>`      | `boolean test(T t)`   | `Collection::isEmpty` | 인수 O, 반환: bool |
| `Function<T,R>`     | `R apply(T t)`        | `Arrays::asList`     | 인수!=반환         |
| `Supplier<T>`       | `T get()`             | `Instant::now`       | 인수 X, 반환 O     |
| `Consumer<T>`         | `void accept(T t)`    | `System.out::println`  | 인수 O, 반환 X     |


