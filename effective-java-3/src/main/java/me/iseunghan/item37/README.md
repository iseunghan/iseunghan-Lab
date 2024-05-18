## ordinal 대신 EnumMap을 사용하라 - 케이스 1
```java
public class Plant {
    enum LifeCycle { ANNUAL, PERENNIAL, BIENNIAL }

    final String name;
    final LifeCycle lifeCycle;

    public Plant(String name, LifeCycle lifeCycle) {
        this.name = name;
        this.lifeCycle = lifeCycle;
    }

    @Override
    public String toString() {
        return name;
    }
}
```
식물의 이름과 상태를 가지는 Plant 클래스이다.

### ordinal은 절대 사용하지 마라
```java
public class BadPractice_1 {
    public static void main(String[] args) {
        Set<Plant>[] plantsByLifeCycle = (Set<Plant>[]) new Set[Plant.LifeCycle.values().length];
        for (int i = 0; i < plantsByLifeCycle.length; i++) {
            plantsByLifeCycle[i] = new HashSet<>();
        }

        List<Plant> garden = List.of(
                new Plant("p1", Plant.LifeCycle.ANNUAL),
                new Plant("p2", Plant.LifeCycle.BIENNIAL),
                new Plant("p3", Plant.LifeCycle.PERENNIAL)
        );
        for (Plant p : garden) {
            plantsByLifeCycle[p.lifeCycle.ordinal()].add(p);    // *만약 LifeCycle 중간에 데이터가 추가된다면? ordinal 일관성을 보장할 수 있는가?
        }

        for (int i = 0; i < plantsByLifeCycle.length; i++) {
            System.out.printf("%s: %s%n", Plant.LifeCycle.values()[i], plantsByLifeCycle[i]);
        }
    }
}
```
자세히 살펴봐야 할 코드는 아래와 같다.
```java
for (Plant p : garden) {
    plantsByLifeCycle[p.lifeCycle.ordinal()].add(p);    // *만약 LifeCycle 중간에 데이터가 추가된다면? ordinal 일관성을 보장할 수 있는가?
}
```
위 코드에서 LifeCycle의 oridnal 즉 순서를 가지고 배열의 인덱스에 식물을 추가하고 있다.
ordinal을 배열의 인덱스로 활용하다니 머리를 좀 굴린 것 같다. 하지만 진짜일까?

만약 LifeCycle을 누가 앞에서부터 아니면 중간에 원소를 추가한다면 어떻게 될까?
위 코드는 그 순간 망가지게 된다.

### 해결책 - EnumMap을 사용하라
```java
public class BadPractice_1_solution {
    public static void main(String[] args) {
        Map<Plant.LifeCycle, Set<Plant>> plantsByLifeCycle = new EnumMap<>(Plant.LifeCycle.class);

        List<Plant> garden = List.of(
                new Plant("p1", Plant.LifeCycle.ANNUAL),
                new Plant("p2", Plant.LifeCycle.BIENNIAL),
                new Plant("p3", Plant.LifeCycle.PERENNIAL)
        );
        for (Plant.LifeCycle lc : Plant.LifeCycle.values()) {
            plantsByLifeCycle.put(lc, new HashSet<>()); // *기존 ordinal과는 확연하게 달라서 변경에도 유연하다.
        }
        for (Plant p : garden) {
            plantsByLifeCycle.get(p.lifeCycle).add(p);
        }
        System.out.println(plantsByLifeCycle);
    }
}
```
ordinal에서 EnumMap을 사용해서 LifeCycle을 키값으로 사용했다.
```java
for (Plant.LifeCycle lc : Plant.LifeCycle.values()) {
    plantsByLifeCycle.put(lc, new HashSet<>()); // *기존 ordinal과는 확연하게 달라서 변경에도 유연하다.
}
```
식물의 LifeCycle을 가지고 EnumMap의 키값을 찾아서 해당 식물을 등록시킨다.
이렇게되면 LifeCycle이 앞이건 중간이건 마지막이건 추가된다해도 이 코드는 절대적으로 안전하게 된다.

## 이중 Enum에서는 어떻게 될까?
```java
public enum BadPractice_Phase {
    SOLID, LIQUID, GAS;

    public enum Transition {
        MELT, FREEZE, BOIL, CONDENSE, SUBLIME, DEPOSIT;

        private static final Transition[][] TRANSITIONS = {
                {null, MELT, SUBLIME},
                {FREEZE, null, BOIL},
                {DEPOSIT, CONDENSE, null}
        };

        public static Transition from(BadPractice_Phase from, BadPractice_Phase to) {
            return TRANSITIONS[from.ordinal()][to.ordinal()];   // *ordinal을 사용하면 Phase의 값이 추가되면 어떻게 대응할 것인지?
        }
    }
}
```
상태들이 있고, 해당 상태들끼리의 연관관계를 Transition이라고 정했다.
조금 짱구를 굴려가지고 Phase의 순서들을 가지고 Transition 내부에 이중 배열을 구성해서 이전상태->이후상태의 인덱스를 가지고 어떤 상태로 변했는지를 구할 수 있게 구성했다.
ordinal을 가지고 이중 배열의 인덱스를 찾아내서 값을 구하다니 확실히 창의적인 방법이다. 하지만 이 코드는 머지않아 망가지게 된다.

일단 Phase 원소가 추가될 떄마다 엄청나게 헷갈리고 늘어나는 이중 배열을 관리해줘야 한다. 지금은 몇개 안되지만 상태가 100개가 넘어간다면? 끔찍하다!
게다가 Phase를 추가하는 위치에 따라서 기존 Transition이 망가진다.

### 이중 EnumMap을 이용해서 해결할 수 있다.
```java
public enum BestPractice_Phase {
    SOLID, LIQUID, GAS;

    public enum Transition {
        MELT(SOLID, LIQUID), FREEZE(LIQUID, SOLID), BOIL(LIQUID, GAS), CONDENSE(GAS, LIQUID), SUBLIME(SOLID, GAS), DEPOSIT(GAS, LIQUID);

        private final BestPractice_Phase from;
        private final BestPractice_Phase to;

        Transition(BestPractice_Phase from, BestPractice_Phase to) {
            this.from = from;
            this.to = to;
        }

        private static final Map<BestPractice_Phase, Map<BestPractice_Phase, Transition>> m = Stream.of(values())
                .collect(groupingBy(
                                t -> t.from,
                                () -> new EnumMap<>(BestPractice_Phase.class),
                                toMap(t -> t.to, t -> t, (x, y) -> y, () -> new EnumMap<>(BestPractice_Phase.class))
                        )
                );

        public static Transition from(BestPractice_Phase from, BestPractice_Phase to) {
            return m.get(from).get(to);
        }
    }
}
```

```java
MELT(SOLID, LIQUID)
```
상태를 가지고 어떤 상태로 변했는지에 대한 정보를 Enum으로 묶어서 구성했다.

```java
private static final Map<BestPractice_Phase, Map<BestPractice_Phase, Transition>> m = Stream.of(values())
.collect(groupingBy(
                t -> t.from,
                () -> new EnumMap<>(BestPractice_Phase.class),
                toMap(t -> t.to, t -> t, (x, y) -> y, () -> new EnumMap<>(BestPractice_Phase.class))
        )
);
```
이 부분이 가장 복잡한데.. 현재 Transition을 순회하면서 EnumMap을 구성하도록 하였다. 이렇게 초기화를 해두면, 아래 from()를 이용해서 값을 빠르게 찾아낼 수 있다.
```java
public static Transition from(BestPractice_Phase from, BestPractice_Phase to) {
    return m.get(from).get(to);
}
```

