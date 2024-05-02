### Enum을 이용해서 간단한 계산기 기능을 구현할 수 있다.
Enum은 완전한 클래스이기 때문에 abstract 메서드를 통해 구현을 강제할 수 있다는 점을 이용할 것이다.

```java
public enum Operation {
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
    TIMES("-") {
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
    },
    ;

    private final String symbol;

    Operation(String symbol) {
        this.symbol = symbol;
    }

    public abstract double apply(double x, double y);
}
```
위 코드를 살펴보면, abstract 메서드를 통해 두 변수를 계산하는 메서드를 구현하게끔 강제했다.

```java
PLUS("+") {
    @Override
    public double apply(double x, double y) {
        return x + y;
    }
}
```
각 계산타입마다 계산 로직을 구현해주면 끝이다. 만약 다른 연산을 추가하고 싶다면 상수를 하나 추가해서 내부 로직만 구현해주면 끝이다!

---

### 내부 중첩 Enum을 이용해 Switch-Case 문을 제거해보자
```java
public enum PayrollDay_with_switch {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY;

    private static final int MINS_PER_SHIFT = 8 * 60;

    int pay(int minutesWorked, int payRate) {
        int basePay = minutesWorked * payRate;

        int overtimePay;
        switch (this) {
            case SATURDAY, SUNDAY -> overtimePay = basePay / 2;
            default -> overtimePay = minutesWorked <= MINS_PER_SHIFT ? 0 : (minutesWorked - MINS_PER_SHIFT) * payRate / 2;
        }
        return basePay + overtimePay;
    }
}
```
위 코드는 급여를 계산하는 Enum을 구현한 것이다. 만약 여기서 공가나 다른 근무 형태를 추가해야한다면 어떻게 해야할까? ENUM 상수를 추가해주고 그에 맞는 switch 문 내부에 로직을 구성해야 할 것이다. 생각만해도 끔찍하다. 혹여나 이 로직을 추가하는 것을 깜빡하는 순간 급여는 default 케이스문에 걸려 엉뚱하게 계산될 것이다.
이 문제점은 내부 중첩 ENUM을 이용해서 쉽게 해결할 수 있다.

```java
public enum PayrollDay_graceful {
    MONDAY(WEEKDAY), TUESDAY(WEEKDAY), WEDNESDAY(WEEKDAY), THURSDAY(WEEKDAY), FRIDAY(WEEKDAY), SATURDAY(WEEKEND), SUNDAY(WEEKEND);

    private final PayType payType;

    PayrollDay_graceful(PayType payType) {
        this.payType = payType;
    }

    int pay(int minutesWorked, int payRate) {
        return payType.pay(minutesWorked, payRate);
    }

    enum PayType {
        WEEKDAY {
            @Override
            int overtimePay(int minsWorked, int payRate) {
                return minsWorked <= MINS_PER_SHIFT ? 0 : (minsWorked - MINS_PER_SHIFT) * payRate / 2;
            }
        },
        WEEKEND {
            @Override
            int overtimePay(int minsWorked, int payRate) {
                return minsWorked * payRate / 2;
            }
        }
        ;

        abstract int overtimePay(int mins, int payRate);
        private static final int MINS_PER_SHIFT = 8 * 60;

        int pay(int minsWorked, int payRate) {
            int basePay = minsWorked * payRate;
            return basePay + overtimePay(minsWorked, payRate);
        }
    }
}
```
루트 Enum은 내부 Enum을 인스턴스 필드로 가지고 있다. 이 코드의 가장 큰 장점은 근무형태가 추가된다면 PayType에 상수를 추가하고 알맞게 로직을 구현하면 된다.
그리고 그 PayType을 가지고 있는 루트 상수를 추가해주면 끝이다!
