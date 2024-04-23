### 아래 방법으로 풀이를 접근했다.
1. 대소문자, 마침표, 쉼표 등 무시 
2. 전처리: 대소문자, 마침표, 쉼표를 다 없앤다. 
3. 각 단어를 가지고 N-1개를 돌면서 개수 체크 & Set에다가 넣어둠 
   1. 만약 해당 단어가 Set의 키로 존재한다면 -> PASS 
   2. Map을 쓰지 않은 이유 -> Map 보다는 (Set + 전역변수(count, resultString))이 더 효율적이라고 생각했음.
5. 가장 많은 카운트의 단어를 리턴한다.

### 가장 큰 실수
조건에서 잘못 캐치한 부분이 있는데
> paragraph consists of English letters, space ' ', or one of the symbols: "!?',;.".

> 단락은 영어 문자, 공백 ' ' 또는 기호 중 하나로 구성됩니다: "!?',;.".

문자 또는 공백 또는 기호들이 나오면 단락으로 구분한다고 나와있다.
책에서는 구두점(마침표, 쉼표 등)은 무시한다고 나와있어서 이 부분을 나중에서야 알게되었다. ~~(내 30분..)~~


### 책은 다음과 같이 풀이한다.
1. 정규표현식으로 문장을 전처리한다.
2. Map(key:String:문자, value:Integer:카운트) 자료구조를 채택했다.
3. 단어들을 공백으로 split 하여 For문으로 순회하며
   1. 금지 단어인지 체크한다.
   2. map에 현재 단어의 카운트 1씩 증가시켜준다.
4. 마지막으로 Map을 돌면서 max인 값의 key를 리턴한다.

### 내가 몰랐던 것들
* Array -> List -> Set
```java
final Set<String> ban = new HashSet<>(Arrays.asList(banned));
```

* 정규표현식
```java
paragraph.replaceAll("\\W+", " ").split(" "))
```

* map.getOrDefault()
```java
counts.getOrDefault(s, 0)
```

* Collection.max()
```java
return Collections.max(counts.entrySet(), Map.Entry.comparingByValue()).getKey();
```