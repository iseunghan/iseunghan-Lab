package me.iseunghan.item31;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public class Main {
//    public static void main(String[] args) {
//        Stack<Number> stack = new Stack<>();
//        System.out.println(stack);
//        stack.pushAll(List.of(1,2,3,4,5));
//        System.out.println(stack);
//
//        ArrayList<Number> list = new ArrayList<>();
//        stack.popAll(list);
//        System.out.println(stack);
//        System.out.println(list);
//    }

    public static void main(String[] args) {
        System.out.println("--- Stack (Number) ---");
        Stack<Number> stack = new Stack<>();
        System.out.println(stack);
        stack.pushAll(List.of(1,2,3,4,5));
        System.out.println(stack);

        System.out.println("--- Stack (Object) ---");
        ArrayList<Object> list = new ArrayList<>();
        stack.popAll(list);
        System.out.println(stack);
        System.out.println(list);

        // Set 실습 (interface를 통해 합칠 수 있다)
        System.out.println("--- Set Number(Integer + Double) ---");
        Set<Integer> integers = Set.of(1, 2);
        Set<Double> doubles = Set.of(1.2, 2.4);
        Set<Number> union1 = SetUtil.union(integers, doubles);
        System.out.println(union1);
    }
}
