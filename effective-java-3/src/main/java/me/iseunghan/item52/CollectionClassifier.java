package me.iseunghan.item52;

import java.util.*;

public class CollectionClassifier {
    public static String classify(Set<?> set) {
        return "집합";
    }

    public static String classify(List<?> l) {
        return "리스트";
    }

    public static String classify(Collection<?> c) {
        return "그 외";
    }

    /**
     * instanceof 연산자는 런타임에 검사할 수 있다. 즉, 동적으로 값을 변환할 수 있게 해준다.
     */
    public static String classify_best_practice(Collection<?> c) {
        return c instanceof Set<?> ? "집합" :
                c instanceof List<?> ? "리스트" : "그 외";
    }
}
