package me.iseunghan.item47;

import java.util.Collections;
import java.util.List;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class SubLists {
    public static <E> Stream<List<E>> of(List<E> list) {
        return Stream.concat(
                Stream.of(Collections.emptyList()),
                prefixes(list)                   // prefixes를 통해 먼저 부분집합을 만든뒤
                    .flatMap(SubLists::suffixes) // 각 prefixes의 원소([1], [1,2],..)들을 suffixes에 넣고 부분집합을 만든다. (ex. [1,2] -> [1], [1,2], [2])
        );
    }

    public static <E> Stream<List<E>> prefixes(List<E> list) {
        return IntStream.rangeClosed(1, list.size())
                .mapToObj(end -> list.subList(0, end));
        // 0~1, 0~2, ... , 0~size개의 부분집합이 Stream에 담긴다.
    }

    public static <E> Stream<List<E>> suffixes(List<E> list) {
        return IntStream.range(0, list.size())
                .mapToObj(start -> list.subList(start, list.size()));
        // 0~size, 1~size, 3~size, ... , n~size 개의 부분집합이 Stream에 담긴다.
    }

    public static void main(String[] args) {
        SubLists.prefixes(List.of(1, 2, 3, 4)).forEach(System.out::println);
        System.out.println("-----------------------------------");
        SubLists.suffixes(List.of(1, 2, 3, 4)).forEach(System.out::println);
        System.out.println("-----------------------------------");
        Stream<List<Integer>> listStream = SubLists.of(List.of(1, 2, 3, 4));
        listStream.forEach(System.out::println);
        System.out.println("-----------------------------------");
    }

    /**
     * Console output
     *
     * [1]
     * [1, 2]
     * [1, 2, 3]
     * [1, 2, 3, 4]
     * -----------------------------------
     * [1, 2, 3, 4]
     * [2, 3, 4]
     * [3, 4]
     * [4]
     * -----------------------------------
     * []
     * [1]
     * [1, 2]
     * [2]
     * [1, 2, 3]
     * [2, 3]
     * [3]
     * [1, 2, 3, 4]
     * [2, 3, 4]
     * [3, 4]
     * [4]
     * -----------------------------------
     */
}
