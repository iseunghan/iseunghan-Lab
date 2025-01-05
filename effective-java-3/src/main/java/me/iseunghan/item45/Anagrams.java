package me.iseunghan.item45;

import java.util.*;

import static java.util.stream.Collectors.groupingBy;

/**
 * 과도한 스트림 사용(overused_lambda_func)은 가독성을 나쁘게 하고 유지보수를 어렵게 만든다.
 * 적당한 스트림 사용(best_practice_lambda_func)은 가독성, 성능, 유지보수를 향상시킨다.
 * 그렇다고 일반 반복문(standard_func) 표현이 나쁘다는 것은 아니다.
 */
public class Anagrams {
    public static void main(String[] args) {
        List<String> dictionary = List.of("staple", "aelpst", "petals", "gasrasd", "agafsqw", "qeqetoj", "asfdasd", "asfavaa", "safavaa");
        System.out.println(">> standard_func: ");
        standard_func(dictionary);
        System.out.println(">> overused_lambda_func: ");
        overused_lambda_func(dictionary);
        System.out.println(">> best_practice_lambda_func: ");
        best_practice_lambda_func(dictionary);
    }

    private static void standard_func(List<String> dictionary) {
        Map<String, Set<String>> groups = new HashMap<>();

        for (String word : dictionary) {
            groups.computeIfAbsent(alphabetize(word), (unused) -> new TreeSet<>()).add(word);
        }

        for (Set<String> group : groups.values()) {
            if (!group.isEmpty()) {
                System.out.printf("%d: %s", group.size(), group);
            }
        }
    }

    private static void overused_lambda_func(List<String> dictionary) {
        dictionary.stream()
                .collect(groupingBy(word -> word.chars().sorted()
                        .collect(StringBuilder::new, (sb, c) -> sb.append((char) c), StringBuilder::append).toString()))
                .values().stream()
                .filter(group -> !group.isEmpty())
                .forEach(group -> System.out.printf("%d: %s%n", group.size(), group));
    }

    // 기존 코드보다 훨씬 간결하고 읽기 쉬워졌다! 스트림을 이용해서 불필요한 객체를 선언하지 않아도 되어서 메모리 확보에도 도움을 준다!
    private static void best_practice_lambda_func(List<String> dictionary) {
        dictionary.stream()
                .collect(groupingBy(Anagrams::alphabetize))
                .values().stream()
                .filter(group -> !group.isEmpty())
                .forEach(group -> System.out.printf("%d: %s%n", group.size(), group));
    }

    private static String alphabetize(String s) {
        char[] charArray = s.toCharArray();
        Arrays.sort(charArray);
        return new String(charArray);
    }
}
