package me.iseunghan.item49;

import java.math.BigInteger;
import java.util.Objects;

/**
 * 메서드는 범용적으로 만들되 한가지 일만 하게끔 설계해야 한다.
 */
public class BestPracticeMethod {

    /**
     * (현재 값 mod m) 값을 반환한다. 이 메서드는 항상 음이 아닌 BigInteger를 반환하다는 점에서 remainer 메서드와 다르다.
     * @param m 계수(양수여야 한다.)
     * @return 현재 값 mod m을 한 결과 값
     * @throws ArithmeticException m이 0q보다 작거나 같으면 발생한다.
     */
    public BigInteger mod(BigInteger m) {
        if (m.signum() <= 0) throw new ArithmeticException("계수(m)는 양수여야 합니다. " + m);
        // FIXME: 다 좋은데 m이 null인 경우를 생각하지 못했다..!
        // .. 계산 수행
        return m;
    }

    public static void main(String[] args) {
//        nullCheck1();
        nullCheck2(null, -10, -1);
    }

    static void nullCheck1() {
        // null을 포함한 매개변수를 예외처리하는 방법 1) Objects.requireNonNull
        String s = null;
        s = Objects.requireNonNull(s, "s는 null일 수 없습니다.");
        /**
         * Exception in thread "main" java.lang.NullPointerException: s는 null일 수 없습니다.
         * 	at java.base/java.util.Objects.requireNonNull(Objects.java:235)
         * 	at me.iseunghan.item49.BestPracticeMethod.main(BestPracticeMethod.java:24)
         */
        System.out.println(s);
    }

    static void nullCheck2(long[] a, int offset, int length) {
        // null을 포함한 매개변수를 예외처리하는 방법 2) assert
        assert a != null;
        assert offset >= 0 && offset <= a.length;
        assert length >= 0 && offset <= a.length - offset;
        // 계산 수행..
    }
}
