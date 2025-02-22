package me.iseunghan.item53;

public class ArgsBestPractice {
    static int sum(int... args) {
        int sum = 0;
        for (int arg : args) {
            sum += arg;
        }
        return sum;
    }

    static int min_bad_practice(int...args) {
        if (args.length == 0) {
            throw new IllegalArgumentException("인수가 1개 이상 필요합니다.");
        }
        int min = Integer.MAX_VALUE;
        for (int arg : args) {
            min = Math.min(min, arg);
        }
        return min;
    }

    /**
     * 가변인수를 어쩔수없이 써야한다면, 90%이상 매개변수를 3개 이하로 사용한다는 것을 파악했다면 다음과 같이 최적화를 고려할 수 있다.
     * 대부분에 상황에서는 의미없는 최적화일테지만, 꼭 필요한 특수상황에서는 가뭄의 단비일지어다..
     */
    static void foo() {}
    static void foo(int a) {}
    static void foo(int a, int b) {}
    static void foo(int a, int b, int c) {}
    static void foo(int a, int b, int c, int... rest) {}

    static int min_best_practice(int firstArg, int...args) {
        int min = firstArg;
        for (int arg : args) {
            min = Math.min(min, arg);
        }
        return min;
    }

    public static void main(String[] args) {
        System.out.println(sum());                // 0
        System.out.println(sum(1, 2, 3));  // 6

        System.out.println(min_bad_practice());              // java.lang.IllegalArgumentException: 인수가 1개 이상 필요합니다.
        System.out.println(min_best_practice(1,2,3));    // 1
    }
}
