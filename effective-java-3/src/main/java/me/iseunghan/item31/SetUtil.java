package me.iseunghan.item31;

import java.util.HashSet;
import java.util.Set;

public class SetUtil {
    public static <E> Set<E> union(Set<? extends E> s1, Set<? extends E> s2) {
        Set<E> result = new HashSet<>();
        result.addAll(s1);
        result.addAll(s2);
        return result;
    }
}
