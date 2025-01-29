package me.iseunghan.item61;

public class Boxing_UnBoxing {
    public static void main(String[] args) {
        boxing_Equals();
    }
    static void boxing_error() {
        Integer i = null;

        if (i == 42) {  // occur NPE!!
            System.out.println("Boxing error"); // not printed
        }
    }

    /**
     * new Integer은 새로운 객체를 반환한다. 즉, == 연산으로는 비교가 불가하다.
     * 하지만, equals는 int 비교와 동일하게 동작한다.
     *
     * Integer.valueOf 내부에는 new Integer를 사용한다. 근데 왜 true가 나오는 것일까?
     * 아래는 IntgerCache를 일부 코드를 발췌한 것이다.
     *
     * private static class IntegerCache {
     *         static final int low = -128;
     *         static final int high;
     *         static final Integer[] cache;
     *         static Integer[] archivedCache;
     *         ...
     * }
     * 정적 팩토리를 통해 캐싱을 하여 매번 같은 객체를 만든 것이였다. 그렇기 때문에 primitive 타입과 동일하게 동작할 수 있었다.
     */
    static void boxing_Equals() {
        Integer a = new Integer(42);
        Integer b = new Integer(42);
        System.out.println(a == b); // false

        Integer a1 = Integer.valueOf(42);
        Integer b1 = Integer.valueOf(42);
        System.out.println(a1 == b1); // true
    }

    // 굉장히 느리다! 박싱과 언박싱이 계속 일어나 성능에 안좋은 영향을 미친다.
    static void box_unbox_is_effect_to_performance() {
        Long sum = 0L;
        for (long i = 0; i <= Integer.MAX_VALUE; i++) {
            sum += i;
        }
        System.out.println(sum);
    }
}
