package me.iseunghan.item58;

import java.util.Iterator;
import java.util.List;

public class UseForEach {

    // 1-0. for loop을 이용해 Collection을 순회하는 방법
    void ex_iterator_for_loop() {
        List<Integer> list = List.of(1, 2, 3);
        for (Iterator<Integer> i = list.iterator(); i.hasNext(); ) {
            Integer next = i.next();
            // do-something..
        }
    }

    // 1-1. 배열은 index 방식이 더 편할 수도 있다.
    void ex_index_for_loop() {
        int[] ints = {1, 2, 3};
        for (int i = 0; i < ints.length; i++) {
            int num = ints[i];
            // do-something..
        }
    }

    // 1-2. Collection은 for-each를 사용하는게 버그 예방에 좋다.
    void ex_enhanced_for_loop() {
        List<Integer> list = List.of(1, 2, 3);
        for (Integer next : list) {
            // do-something..
        }
    }

}
