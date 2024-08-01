## 아이템 38. 확장할 수 있는 열거 타입이 피요하면 인터페이스를 사용하라
열거타입은 인터페이스 확장을 사용할수가 없을까? 대부분의 열거타입을 확장하는 케이스는 불필요하지만, 한가지 유용한 케이스가 있다.

### Operation을 확장 가능 열거 타입으로 흉내내보자.
```java
public interface Operation {
    double apply(double x, double y);
}
```

### 기본 연산에 대해서
```java
package me.iseunghan.item38;

public enum BasicOperation implements Operation {
    PLUS("+") {
        @Override
        public double apply(double x, double y) {
            return x + y;
        }
    },
    MINUS("-") {
        @Override
        public double apply(double x, double y) {
            return x - y;
        }
    },
    TIMES("*") {
        @Override
        public double apply(double x, double y) {
            return x * y;
        }
    },
    DIVIDE("/") {
        @Override
        public double apply(double x, double y) {
            return x / y;
        }
    }
    ;

    private final String symbol;

    BasicOperation(String symbol) {
        this.symbol = symbol;
    }

    @Override
    public String toString() {
        return symbol;
    }
}

```

### 확장 연산에 대해서
```java
package me.iseunghan.item38;

public enum ExtendedOperation implements Operation {
    EXP("^") {
        @Override
        public double apply(double x, double y) {
            return Math.pow(x, y);
        }
    },
    REMAINDER("%") {
        @Override
        public double apply(double x, double y) {
            return x % y;
        }
    },
    ;

    private final String symbol;

    ExtendedOperation(String symbol) {
        this.symbol = symbol;
    }

    @Override
    public String toString() {
        return symbol;
    }
}

```

위 예제로 살펴볼 수 있듯 -> 필요할 때마다 Operation을 확장해서 열거 타입을 생성하면 된다. 근데 왜 굳이 나누는지 모르겠는데 예상해보자면, 권한에 따라서 (혹은 필요성에 따라) 접근을 제한시킬 수 있어서가 아닐까?

### 클라이언트 코드
```java
package me.iseunghan.item38;

import java.util.Arrays;
import java.util.Collection;

public class Client {
    public static void main(String[] args) {
        double x = 2.0;
        double y = 1.0;
        test(ExtendedOperation.class, x, y);
        test2(BasicOperation.class, x, y);
        test3(Arrays.asList(ExtendedOperation.values()), x, y);
    }

    // 이건 Enum이 아닌 타입이 들어올 가능성이 있다.
    private static void test(Class<? extends Operation> opEnumType, double x, double y) {
        for (Operation op : opEnumType.getEnumConstants()) {
            System.out.printf("%f %s %f = %f%n", x, op, y, op.apply(x, y));
        }
    }

    private static <T extends Enum<T> & Operation> void test2(Class<T> opEnumType, double x, double y) {
        for (Operation op : opEnumType.getEnumConstants()) {
            System.out.printf("%f %s %f = %f%n", x, op, y, op.apply(x, y));
        }
    }

    // 이것도 마찬가지인데?
    private static void test3(Collection<? extends Operation> opSet, double x, double y) {
        for (Operation op : opSet) {
            System.out.printf("%f %s %f = %f%n", x, op, y, op.apply(x, y));
        }
    }
}

```
클라이언트에서는 두가지 방법으로 파라미터를 받을 수 있다.
1. 제네릭 타입
2. 한정적 와일드카드 타입

2번째 방식에는 특정 연산에 대해서 enumSet, enumMap을 사용할 수 없다. (특정 연산이 무엇을 뜻하는지 잘 모르겠음)
```java
test3(EnumSet.allOf(BasicOperation.class), x, y);
test3(EnumSet.allOf(ExtendedOperation.class), x, y);
```