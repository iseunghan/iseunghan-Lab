package book.ch6.sub3;

import org.junit.jupiter.api.Test;

import java.util.*;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MySolution {

    @Test
    void test() {
        Solution solution = new Solution();
        String[] result = solution.reorderLogFiles(new String[]{"dig1 8 1 5 1", "let1 art can", "dig2 3 6", "let2 own kit dig", "let3 art zero"});
        assertEquals(Arrays.toString(result), "[let1 art can, let3 art zero, let2 own kit dig, dig1 8 1 5 1, dig2 3 6]");
    }

    static class Solution {
        public String[] reorderLogFiles(String[] logs) {

            List<String> letters = new ArrayList<>(logs.length);
            List<String> digits = new ArrayList<>(logs.length);

            Arrays.stream(logs)
                    .filter(this::isDigitLog)
                    .forEach(digits::add);

            Arrays.stream(logs)
                    .filter(s -> !isDigitLog(s))
                    .sorted((s1, s2) -> {
                        int result = s1.substring(s1.indexOf(" ") + 1).compareTo(s2.substring(s2.indexOf(" ") + 1));
                        if (result == 0) {
                            return s1.split(" ")[0].compareTo(s2.split(" ")[0]);
                        }
                        return result;
                    }).forEach(letters::add);

            System.out.println(letters);
            System.out.println(digits);
            letters.addAll(digits);
            return letters.toArray(new String[logs.length]);
        }

        private boolean isDigitLog(String s) {
            return s.split(" ")[1].charAt(0) < 97;
        }
    }

    @Test
    void stringTest() {
        String s = "log1 abc test";
        String[] s_2 = s.split(" ", -2);
        String[] s_1 = s.split(" ", -1);
        String[] s0 = s.split(" ");
        String[] s1 = s.split(" ", 1);
        String[] s2 = s.split(" ", 2);
        String[] s3 = s.split(" ", 3);
        String[] s4 = s.split(" ", 4);

        System.out.println("s_2 = " + Arrays.toString(s_2));
        System.out.println("s_1 = " + Arrays.toString(s_1));
        System.out.println("s1 = " + Arrays.toString(s1));
        System.out.println("s2 = " + Arrays.toString(s2));
        System.out.println("s3 = " + Arrays.toString(s3));
        System.out.println("s4 = " + Arrays.toString(s4));
    }

    @Test
    void stringTest1() {
        String[] strings = {"a", "b", "c"};
        String[] strings2 = {"c", "b", "a"};
        System.out.println("a".compareTo("b"));
        System.out.println("a".compareTo("a"));
        System.out.println("d".compareTo("c"));
        System.out.println("-------------------");

        Arrays.stream(strings)
                .sorted(String::compareTo)
                .forEach(System.out::println);
        System.out.println("-------------------");
        Arrays.stream(strings2)
                .sorted(String::compareTo)
                .forEach(System.out::println);
    }

    @Test
    void stringTest2() {
        int[] ints = {1,2,3};
        int[] ints2 = {5,4,3};
        System.out.println(Integer.compare(1, 2));
        System.out.println(Integer.compare(1, 1));
        System.out.println(Integer.compare(3, 2));
        System.out.println("-------------------");

        Arrays.stream(ints)
                .sorted()
                .forEach(System.out::println);
        System.out.println("-------------------");
        Arrays.stream(ints2)
                .sorted()
                .forEach(System.out::println);
    }
}
