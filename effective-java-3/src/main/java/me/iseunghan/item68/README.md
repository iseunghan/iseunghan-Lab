# 일반적으로 통용되는 명명 규칙을 따르라
### 패키지는 도메인을 뒤집어서 사용한다.  
예를 들어 구글이라면, `google.com` -> `com.google`로 시작

### 패키지명은 약어를 추천한다.
일반적으로 8자 이하로 사용한다.
- utilities보단 util 처럼 의미가 통하는 약어를 사용하자.
- 너무 길다면 단어의 첫글자만 따서 사용하라. `ex. java.awt (Abstract Window Toolkit)`

### 클래스와 인터페이스의 이름은 하나의 이상 단어로 이뤄진다.
- 여러 단어라면 첫글자만 대문자로 사용하자
  - `ex. HttpUrl (O), HTTPURL (X)`
- 객체를 생성할 수 있는 클래스는 단수 명사나 명사구를 사용한다.
  - ex. Thread, PriorityQueue...
- 객체를 생성할 수 없는 클래스는 복수 명사로 짓는다.
  - ex. Collectors, Collections,...
- 인터페이스는 클래스와 같이 짓거나 able, ible로 끝나는 형용사로도 짓는다.
  - ex. Collection, Comparator, ...
  - ex. Runnable, Iterable, Accessible,....

### 메서드는 첫글자는 소문자, 단어의 첫 글자는 대문자로 시작한다.
- ex. remove, removeElement와 같이 사용한다.
- 행위를 타나내는 동사 또는 목적을 나타내는 동사구를 사용한다.
  - ex. append, drawImage, ...
- boolean을 리턴하는 메서드는 보통 is로 시작하거나 has로 시작한다.
  - ex. isDigit, hasValue, ...
- 어떤 타입을 얻을 때 get으로 많이들 사용하는데 편한쪽을 선택하면 될 것 같다.
- 특별한 케이스
  - 새로운 인스턴스로 변환하는 메서드는 toType으로 짓는다. `ex. toList`
  - 객체의 내용을 새로운 뷰로 반환할 때는 asType으로도 짓는다. `ex. asList`
  - 정적 팩터리 이름은 보통 of, newInstance 등등을 사용한다.

### 상수 필드는 대문자와 밑줄로 단어를 구분한다.
- `ex. MAX_VALUE, INIT_NUM`

### 타입 매개변수는 한글자를 사용한다.
- 임의의 타입: T
- 컬렉션 원소: E
- 맵의 키와 값: K, V
- 예외: X
- 메서드 반환타입: R
- 그 외 타입의 시퀀스들: T, U, V, T1, T2, T3, ...
