package me.iseunghan.item62;

import java.util.HashMap;
import java.util.Map;

public class ThreadLocal2 {
    private ThreadLocal2() {}
    private static final Map<Key, Object> store = new HashMap<>();
    public static class Key {}

    // static + 매번 새로운 객체를 생성하여 `유니크 키` 생성
    public static Key getKey() {
        return new Key();
    }

    public static void set(Key key, Object value) {
        // do-something
        store.put(key, value);
    }

    public static Object get(Key key) {
        // do-something
        return store.get(key);
    }
}
