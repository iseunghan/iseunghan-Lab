package item32;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public class VarargsBestPracticeUse {
    public static void main(String[] args) {
        List<String> strings = pickTwo("s1", "s2", "s3");
        System.out.println(strings);
    }

    static <T> List<T> pickTwo(T a, T b, T c) {
        System.out.println("pickTwo -> a: " + a.getClass() + " b: " + b.getClass() + " c: " + c.getClass());
        switch (ThreadLocalRandom.current().nextInt(3)) {
            case 0: return List.of(a, b);
            case 1: return List.of(b, c);
            case 2: return List.of(c, a);
        }
        throw new AssertionError();
    }
}
