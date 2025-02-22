package me.iseunghan.item55;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.function.Supplier;

public class OptionalExample {
    // ex.1. Optional이 없었던 시절, 없으면 예외를 발생하거나 null을 반환함.
    public static <T extends Comparable<T>> T max(List<T> list) {
        if (list.isEmpty()) {
            throw new IllegalArgumentException("List is empty");
        }
        return list.stream().min(Comparator.naturalOrder()).get();
    }

    // ex.2. Optional을 반환할 때, 클라이언트에서는 Optional을 처리하면 된다.
    public static <T extends Comparable<T>> Optional<T> max_with_optional(List<T> list) {
        return list.stream().max(Comparator.naturalOrder());
    }

    // ex.3. 클라이언트가 Optional을 처리하지 않아서 편리하다. 2번,3번 중 편한것을 상황에 따라 골라쓰자
    public static <T extends Comparable<T>> T max_with_optional(List<T> list, Supplier<T> supplier) {
        return list.stream().max(Comparator.naturalOrder()).orElseGet(supplier);
    }

    public static void main(String[] args) {
        intListTest();
        System.out.println("-----------------");
        emptyTest();
        System.out.println("-----------------");
        streamOptional();
    }

    private static void intListTest() {
        List<Integer> intList = List.of(10, 132, 124, 12);

        try {
            max(intList);
            System.out.println("max(emptyList) has success");
        } catch (IllegalArgumentException e) {
            System.out.println("max(emptyList) has thrown exception: " + e.getMessage());
        }
        System.out.println(max_with_optional(intList).isPresent());
        System.out.println(max_with_optional(intList, () -> 0));
    }

    public static void emptyTest() {
        List<Integer> emptyList = Collections.emptyList();

        try {
            max(emptyList);
            System.out.println("max(emptyList) has success");
        } catch (IllegalArgumentException e) {
            System.out.println("max(emptyList) has thrown exception: " + e.getMessage());
        }
        System.out.println(max_with_optional(emptyList).isEmpty());
        System.out.println(max_with_optional(emptyList, () -> 0) == 0);
    }

    public static void streamOptional() {
        Optional<String> str = Optional.of("abc");
        Optional<String> str2 = Optional.empty();
        System.out.println(str.map(String::toUpperCase).map(String::trim).orElse("None"));
        System.out.println(str2.map(String::toUpperCase).map(String::trim).orElse("None"));
    }
}
