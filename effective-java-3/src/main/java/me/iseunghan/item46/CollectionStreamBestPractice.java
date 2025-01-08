package me.iseunghan.item46;

import me.iseunghan.item34.Operation;

import java.util.*;
import java.util.function.BinaryOperator;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.util.Map.Entry.comparingByValue;

public class CollectionStreamBestPractice {

    void example1_worst_practice() {
        // given
        List<String> words = List.of("word", "word2", "word1", "word1", "word", "word");

        // then
        HashMap<String, Long> freq = new HashMap<>();
        words.forEach(word -> {
            freq.merge(word.toLowerCase(), 1L, Long::sum);
        });
    }

    void example1_best_practice() {
        // given
        List<String> words = List.of("word", "word2", "word1", "word1", "word", "word");

        // then
        // 훨씬 간결하고 잘 작성된 스트림은 행위가 자연스럽게 읽힌다.
        Map<String, Long> freq = words.stream()
                .collect(Collectors.groupingBy(String::toLowerCase, Collectors.counting()));
                // grouping을 해서 map으로 만들건데, 키값은 소문자 문자열이고 값은 갯수이다.
    }

    void freq_word_limit_10() {
        // given
        HashMap<String, Long> freq = new HashMap<>();

        // then
        List<String> list = freq.entrySet().stream()
                .sorted(comparingByValue(Comparator.reverseOrder()))    // comparingByValue는 Stream API에서 제공하는 Entry의 value끼리 비교할 수 있는 Comparator 함수이다.
                // 인자에는 람다식(`(o1, o2) -> {비교식}`)이 들어가는데, 내림차순으로 정렬하고자 하면 o2.getValue().compare(o1.getValue())를 하면 된다. 하지만 이것 또한 Comparator에서 제공하는 reverseOrder()가 있다.
                .limit(10)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());

        List<String> list2 = freq.keySet().stream()
                .sorted(Comparator.comparing(freq::get).reversed())
                .limit(10)
                .toList();
    }

    static void practice_collector() {
        // (case1) toMap 수집기를 이용한 열거 타입 상수를 맵으로 변환
        Map<String, Operation> stringToEnum = Stream.of(Operation.values())
                .collect(Collectors.toMap(Object::toString, e -> e));


        // (case2) toMap 수집기를 이용해 merge 기능을 활용한 최대값만 뽑기 (Album 클래스를 만들기 귀찮아서 이중배열로 예제를 구현해봤다)
        String[][] albums = {{"a1", "10"}, {"a1", "30"}, {"a2", "20"}, {"a3", "40"}, {"a2", "10"}, {"a3", "25"}};

        Map<String, Integer> collect = Arrays.stream(albums)
                .collect(Collectors.toMap(s -> s[0], s -> Integer.valueOf(s[1]), BinaryOperator.maxBy(Comparator.comparingInt(Integer::valueOf))));
                                // toMap(keyMapper, valueMapper, (oldVal, newVal) -> newVal)

        System.out.println(collect);    // {a1=30, a2=20, a3=40}


        // groupingBy -> return Map(grouped List)
        List<String> words = List.of("4123", "2423", "1234", "3131", "2234");
        Map<String, List<String>> alphabetMap = words.stream().collect(Collectors.groupingBy(s -> alphabetize(s)));
        System.out.println(alphabetMap);    // {1234=[4123, 1234], 2234=[2423, 2234], 1133=[3131]}

        // groupingBy -> return Map(downstream: 여기선 개수 계산)
        Map<String, Long> countMap = words.stream().collect(Collectors.groupingBy(s -> alphabetize(s), Collectors.counting()));
        System.out.println(countMap);   // {1234=2, 2234=2, 1133=1}

        // groupingBy -> return Map by MapFactory(2th argument)
        TreeMap<String, Long> treeMap = words.stream().collect(Collectors.groupingBy(s -> alphabetize(s), TreeMap::new, Collectors.counting()));
        System.out.println(treeMap);   // {1133=1, 1234=2, 2234=2} 정렬된 상태로 반환!
    }

    public static String alphabetize(String s) {
        char[] arr = s.toCharArray();
        Arrays.sort(arr);
        return new String(arr);
    }
}
