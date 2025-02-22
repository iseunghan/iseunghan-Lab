package me.iseunghan.item52;

import java.util.*;

/**
 * override(재정의) 메서드는 동적으로 정해진다. (런타임)
 * overload(다중정의) 메서드는 정적으로 정해진다. (컴파일타임)
 */
public class OverloadingExample {
    public static void main(String[] args) {
        overloading_is_selected_compileTime();
        System.out.println("------------------------------");
        overloading_can_selected_runtime();
        System.out.println("------------------------------");
        overriding_is_selected_runtime();
    }

    /**
     * 오버로딩은 컴파일 타임에 정해진다. 즉, Collection 타입으로 뽑았기 때문에 전부 Collection 매개변수로 받는 함수로 정해져버린 것이다.
     */
    public static void overloading_is_selected_compileTime() {
        Collection<?>[] collections = {
                new HashSet<>(), new ArrayList<>(), new HashMap<>().values()
        };

        for (Collection<?> collection : collections) {
            System.out.println(CollectionClassifier.classify(collection));
            // 그 외 * 3
        }
    }

    public static void overloading_can_selected_runtime() {
        Collection<?>[] collections = {
                new HashSet<>(), new ArrayList<>(), new HashMap<>().values()
        };

        for (Collection<?> collection : collections) {
            System.out.println(CollectionClassifier.classify_best_practice(collection));
            // 집합, 리스트, 그 외
        }
    }

    /**
     * 재정의(override)는 런타임에 정해진다. 마지막에 재정의한 메서드를 실행시킨다.
     */
    public static void overriding_is_selected_runtime() {
        Wine[] wines = {
                new Wine(), new SparklingWine(), new Champagne()
        };

        for (Wine wine : wines) {
            System.out.println(wine.name());
            // 포도주, 발포성 포도주, 샴페인
        }
    }
}
