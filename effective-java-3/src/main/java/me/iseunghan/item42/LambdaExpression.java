package me.iseunghan.item42;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class LambdaExpression {
    public static void main(String[] args) {
        List<String> words = List.of("w", "o", "r", "d");

        // old Expression (익명클래스 - 진짜 오래된 기법)
        Collections.sort(words, new Comparator<String>() {
            @Override
            public int compare(String o1, String o2) {
                return Integer.compare(o1.length(), o2.length());
            }
        });

        // 람다식을 이용
        Collections.sort(words, (o1, o2) -> Integer.compare(o1.length(), o2.length()));
        /**
         * 어떻게 위와 같이 매개변수를 함다식으로 사용할 수 있을까?
         * 실은, Comparator가 FunctionalInterface 이다! 그렇기 때문에 람다식으로 표현할 수 있었던 것..!
         */
        Comparator<String> stringComparator = (o1, o2) -> Integer.compare(o1.length(), o2.length());    // <-- FunctionalInterface 때문에 함수형 프로그래밍이 가능한것.
        Collections.sort(words, stringComparator);

        // 람다식을 생략, 메서드 참조를 이용한 기법
        Collections.sort(words, Comparator.comparingInt(String::length));

        // 리스트 sort api + 메서드 참조
        words.sort(Comparator.comparing(String::hashCode));
    }
}
