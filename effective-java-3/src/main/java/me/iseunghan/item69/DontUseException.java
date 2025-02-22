package me.iseunghan.item69;
// TODO: git commit -m "[effective-java-3] - [item69] 예외는 진짜 예외 상황에서만 사용하라"
/**
 * 예외는 정말 예외인 상황에서만 사용해야지, 정상적인 흐름을 제어하려고 사용하면 안된다. 예외를 사용하면 표준 관용구보다 훨씬 느리게 된다
 */
public class DontUseException {
    public static void main(String[] args) {
        int[] arr = new int[100];
        for (int i = 0; i < 100; i++) {
            arr[i] = i;
        }
        long start = System.nanoTime();
        bad_method(arr);
        System.out.println(System.nanoTime() - start);  // 31208
        start = System.nanoTime();
        best_method(arr);
        System.out.println(System.nanoTime() - start);  // 1583 (무려 약 30배 빠르다!)
    }

    static void bad_method(int[] arr) {
        try {
            int i = 0;
            while (true) {
                int i1 = arr[i++];
            }
        } catch (ArrayIndexOutOfBoundsException e) {
        }
    }

    static void best_method(int[] arr) {
        for (int i : arr) {
            int i1 = i;
        }
    }
}
