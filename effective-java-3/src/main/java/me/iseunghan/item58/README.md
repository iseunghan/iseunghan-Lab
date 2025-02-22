## for문 보다는 for-each를 사용하자

### for문 보다는 for-each가 훨씬 간결하고 버그 예방에도 좋다.
```java
// 1-0. for loop을 이용해 Collection을 순회하는 방법
    void ex_iterator_for_loop() {
        List<Integer> list = List.of(1, 2, 3);
        for (Iterator<Integer> i = list.iterator(); i.hasNext(); ) {
            Integer next = i.next();
            // do-something..
        }
    }

    // 1-1. 배열은 index 방식이 더 편할 수도 있다.
    void ex_index_for_loop() {
        int[] ints = {1, 2, 3};
        for (int i = 0; i < ints.length; i++) {
            int num = ints[i];
            // do-something..
        }
    }

    // 1-2. Collection은 for-each를 사용하는게 버그 예방에 좋다.
    void ex_enhanced_for_loop() {
        List<Integer> list = List.of(1, 2, 3);
        for (Integer next : list) {
            // do-something..
        }
    }
```

### 다음 버그를 찾아보자

```java
import java.util.ArrayList;
import java.util.List;

enum Suit {CLUB, DIAMOND, HEART, SPADE}

enum Rank {ACE, DEUCE, THREE, FOUR, FIVE, ...}
...

static Collection<Suit> suits = Arrays.asList(Suit.values());
static Collection<Rank> ranks = Arrays.asList(Rank.values());

List<Card> deck = new ArrayList<>();
for (Iterator<Suit> i = suits.iterator(); i.hasNext(); )
    for (Iterator<Rank> j = ranks.iterator(); j.hasNext(); )
        deck.add(new Card(i.next(), j.next()));
```
뭐가 문제일까? 바로 `deck.add(new Card(i.next(), j.next()));`가 문제이다.
이 부분에서 원소의 길이가 더 적은 suit가 i.next()로 원소의 길이를 초과해서 불리고 있다. 이는 NoSuchElementException이 발생할 것이다.

해결법은 간단하다. for-each를 사용해라.
```java
for (Suit s : suits)
    for (Rank r : ranks)
        deck.add(new Card(s, r));
```
for-each로 표현하니 참 간결하고 이해하기 쉽다.

### for-each를 사용할 수 없는 3가지 상황
1. 파괴적인 필터링(destructive filtering): 컬렉션을 순회하며 선택된 원소를 제거해야 한다면, remove를 호출하거나 removeIf를 호출해야 한다.
2. 변형(transforming): 리스트나 배열을 순회하면서 그 원소의 값 일부 혹은 전체를 교체해야 한다면 리스트의 반복자나 배열의 인덱스를 사용해야 한다.
3. 병렬 반복(parallel iteration): 여러 컬렉션을 병렬로 순회해야 한다면 각각의 반복자와 인덱스 변수를 사용해 엄격하고 명시적으로 제어해야 한다.
