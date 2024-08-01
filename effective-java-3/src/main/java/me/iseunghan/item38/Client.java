package me.iseunghan.item38;

import java.util.*;

public class Client {
    public static void main(String[] args) {
        double x = 2.0;
        double y = 1.0;
        test(ExtendedOperation.class, x, y);
        test2(BasicOperation.class, x, y);
        test3(Arrays.asList(ExtendedOperation.values()), x, y);
        test3(EnumSet.allOf(BasicOperation.class), x, y);
        test3(EnumSet.allOf(ExtendedOperation.class), x, y);
    }

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

    private static void test3(Collection<? extends Operation> opSet, double x, double y) {
        for (Operation op : opSet) {
            System.out.printf("%f %s %f = %f%n", x, op, y, op.apply(x, y));
        }
    }
}
