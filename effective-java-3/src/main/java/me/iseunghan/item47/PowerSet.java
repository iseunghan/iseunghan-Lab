package me.iseunghan.item47;

import java.util.*;

public class PowerSet {
    public static final <E> Collection<Set<E>> of(Set<E> s) {
        ArrayList<E> src = new ArrayList<>(s);
        if (src.size() > 30) throw new IllegalArgumentException("집합에 원소가 너무 많습니다 (최대 30개). : " + s);

        return new AbstractList<Set<E>>() {
            @Override
            public Set<E> get(int index) {
                Set<E> result = new HashSet<>();
                for (int i = 0; index != 0; i++, index >>= 1) {
                    if ((index & 1) == 1) {
                        result.add(src.get(i));
                    }
                }
                return result;
            }

            // contains, size 함수는 collection을 위해 필요한 메서드!
            @Override
            public int size() {
                return 1 << src.size(); // n의 멱집합은 2^n 개이다.
            }

            @SuppressWarnings("unchecked")
            @Override
            public boolean contains(Object o) {
                return o instanceof Set && src.containsAll((Set<E>) o);
            }
        };
    }

    public static void main(String[] args) {
        Collection<Set<Integer>> sets = of(Set.of(1, 2, 3, 4));
        System.out.println(sets);
    }
}