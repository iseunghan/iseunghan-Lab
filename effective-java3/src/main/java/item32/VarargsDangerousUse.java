package item32;

import java.util.concurrent.ThreadLocalRandom;

public class VarargsDangerousUse {
    public static void main(String[] args) {
        String[] strings = pickTwo("s1", "s2", "s3");
    }

    static <T> T[] pickTwo(T a, T b, T c) {
        System.out.println("pickTwo -> a: " + a.getClass() + " b: " + b.getClass() + " c: " + c.getClass());
        switch (ThreadLocalRandom.current().nextInt(3)) {
            case 0: return toArray(a, b);
            case 1: return toArray(b, c);
            case 2: return toArray(c, a);
        }
        throw new AssertionError();
    }

    static <T> T[] toArray(T... args) {
        System.out.println("toArray -> args: " + args.getClass());
        return args;
    }


}
