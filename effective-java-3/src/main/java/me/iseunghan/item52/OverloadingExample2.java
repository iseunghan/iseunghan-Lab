package me.iseunghan.item52;

import com.sun.source.tree.Tree;

import java.util.*;

public class OverloadingExample2 {
    public static void main(String[] args) {
        Set<Integer> set = new TreeSet<>();
        List<Integer> list = new ArrayList<>();

        for (int i = -3; i < 3; i++) {
            set.add(i);
            list.add(i);
        }

        for (int i = 0; i < 3; i++) {
            set.remove(i);
            list.remove(i);
        }

        System.out.println(set);    // [-3, -2, -1]
        System.out.println(list);   // [-2, 0, 2] -> 왜 일까? -> remove는 다중정의로 인해 혼란을 준다.
        // remove(int): 인덱스의 원소를 제거한다.
        // remove(Object): 해당 값을 가지는 원소를 제거한다.
        // 올바르게 동작하게 한다면 다음과 같이 변경한다. list.remove((Integer) i);
    }
}
