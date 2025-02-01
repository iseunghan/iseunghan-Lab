package me.iseunghan.item64;

import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.util.*;

public class InterfaceCoding {

    static void method1() {
        // 좋은 예. 인터페이스 타입으로 선언
        Set<String> bestExample = new HashSet<>();

        // 나쁜 예. 구체클래스 타입으로 선언
        HashSet<String> badExample = new HashSet<>();

        // 이런식으로 인터페이스 코딩을 하면, 쉽게 구현체를 갈아끼울 수 있다.
        Set<String> bestExample2 = new TreeSet<>();
    }

    static void warningEx() {
        Set<String> orderSet = new LinkedHashSet<>();

        // [기존 로직] orderSet의 순서대로 처리하고 있었다.
        for (String s : orderSet) {
            // do-something
        }

        // WARNING!!! 이제 orderSet은 순서가 보장되지 않게 된다.
        orderSet = new HashSet<>();
        for (String s : orderSet) {
            // 컴파일은 문제없이 되겠지만, 내부 로직이 소리소문없이 박살나게 된다. 즉, 런타임때 버그가 발생할 수 있다..
        }
    }

    // 클래스 타입으로 선언하는 일은 아래 3가지 경우로 최소화해야 유연한 프로그래밍을 할 수 있다..
    static void example() {
        // (1)
        // 값 타입(String, Integer, ..) 은 인터페이스, 추상클래스가 없다.
        String s = "";
        Integer i = 1;
        // Number는 Integer의 상위클래스지만 n.compareTo(1);와 같은 기능들이 불가능하다. Number는 값을 담는 용도로만 제한된다.
        Number n = 1;
        i.compareTo(1);

        // (2)
        // Frmaework에서 지원해주는 OutputStream과 같은 부류는 인터페이스가 없고 추상클래스 타입으로 존재한다.
        // 이럴때는 인터페이스와 같이 추상클래스 타입으로 선언해주는 것이 좋다.
        OutputStream os = new ByteArrayOutputStream();

        // (3)
        // 기능이 적은 상위 클래스인 경우
        PriorityQueue<String> pq = new PriorityQueue<>();
        Queue<String> q = new PriorityQueue<>();
        pq.comparator();
        // 반면에 q.comparator(); 기능은 제공하지 않는다.
    }
}
