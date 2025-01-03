package me.iseunghan.item44;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.BiPredicate;

public class StandardFuncInterface {
    public static void main(String[] args) {
        LinkedHashMap<Object, Object> map = new LinkedHashMap<>();
    }

    // CustomEldestEntryRemovalFunction 인터페이스 보다는 BiPRedicate를 사용하면 된다. 이미 있는 걸 사용하고 정 안될 때 커스텀으로 생성하라.
    public static void putOrRemoveEldestEntry(BiPredicate<Map<Object, Object>, Map.Entry<Object, Object>> p) {
        if (p.equals(true)) {
//            map.removeEldest()
        }
//        map.put(key, value);
    }
}
