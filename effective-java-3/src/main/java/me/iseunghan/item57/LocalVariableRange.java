package me.iseunghan.item57;


import java.util.Iterator;
import java.util.List;

public class LocalVariableRange {

    /**
     * 기본적인 for문
     */
    public static void rangeExample1() {
        List<Integer> list = List.of(1, 2, 3, 4);

        for (Integer i : list) {
            // i를 이용해 뭔가를 한다.
        }
    }

    /**
     * for + iterator 조합 예제
     */
    public static void rangeExample2() {
        List<Integer> list = List.of(1, 2, 3, 4);

        for (Iterator<Integer> i = list.iterator(); i.hasNext(); ) {
            Integer next = i.next();
            System.out.println(next);
            // next를 이용해 뭔가를 한다.
        }
    }

    /**
     * 실수하면, 컴파일타임에는 물론 런타임에도 잡을 수 없는 while문 (개발자의 디버깅이라는 비용이 필요하다)
     */
    public static void rangeExample3() {
        List<Integer> list = List.of(1, 2, 3, 4);
        List<Integer> list2 = List.of(1, 2, 3, 4);

        Iterator<Integer> i = list.iterator();
        while (i.hasNext()) {
            Integer next = i.next();
            // next를 이용해 뭔가를 한다.
        }

        Iterator<Integer> i2 = list2.iterator();
        while (i.hasNext()) {   // BUG! 런타임에도 잡을 수 없는 에러. 디버깅을 꼼꼼히 해봐야 파악할 수 있다.
            Integer next = i.next();
            // next를 이용해 뭔가를 한다.
        }
    }

    /**
     * 실수를 해도, 컴파일타임에 잡을 수 있는 for문
     */
    public static void rangeExample4() {
        List<Integer> list = List.of(1, 2, 3, 4);
        List<Integer> list2 = List.of(1, 2, 3, 4);

        for (Iterator<Integer> i = list.iterator(); i.hasNext(); ) {
            Integer next = i.next();
            // next를 이용해 뭔가를 한다.
        }

        // for문은 이전 while문에 비해 범위가 작기 때문에 컴파일 타임에 에러를 바로 잡을 수 있다.
//        for (Iterator<Integer> i2 = list2.iterator(); i.hasNext(); ) {
//            Integer next = i2.next();
            // next를 이용해 뭔가를 한다.
//        }
    }
}
