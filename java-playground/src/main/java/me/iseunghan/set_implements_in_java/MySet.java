package me.iseunghan.set_implements_in_java;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class MySet {
    public static void main(String[] args) {
        calc_InnerSet();
        calc_LeftOuterSet();
        calc_RightOuterSet();
        calc_OuterSet();
        calc_WholeSet();
    }

    static void calc_InnerSet() {
        List<Integer> a = new ArrayList<>(List.of(1,2,3,4,5));
        List<Integer> b = new ArrayList<>(List.of(2,4,6,8,10));

        a.retainAll(b);
        System.out.println("a,b의 교집합: " + a);
    }

    static void calc_LeftOuterSet() {
        List<Integer> a = new ArrayList<>(List.of(1,2,3,4,5));
        List<Integer> b = new ArrayList<>(List.of(2,4,6,8,10));

        a.removeAll(b);
        System.out.println("a의 차집합: " + a);
    }

    static void calc_RightOuterSet() {
        List<Integer> a = new ArrayList<>(List.of(1,2,3,4,5));
        List<Integer> b = new ArrayList<>(List.of(2,4,6,8,10));

        b.removeAll(a);
        System.out.println("b의 차집합: " + b);
    }

    static void calc_OuterSet() {
        List<Integer> a = new ArrayList<>(List.of(1,2,3,4,5));
        List<Integer> b = new ArrayList<>(List.of(2,4,6,8,10));

        List<Integer> c = new ArrayList<>(a);
        c.retainAll(b);

        a.removeAll(c);
        b.removeAll(c);
        System.out.println("a의 차집합: " + a + ", " + "b의 차집합: " + b);
        a.addAll(b);
        System.out.println("a,b의 차집합: " + a);
    }

    static void calc_WholeSet() {
        List<Integer> a = new ArrayList<>(List.of(1,2,3,4,5));
        List<Integer> b = new ArrayList<>(List.of(2,4,6,8,10));
        a.removeAll(b);

        a.addAll(b);
        Collections.sort(a);
        System.out.println("a,b의 합집합: " + a);
    }
}
