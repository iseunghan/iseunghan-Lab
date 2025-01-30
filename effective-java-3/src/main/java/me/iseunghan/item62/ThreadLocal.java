package me.iseunghan.item62;

import java.util.HashMap;
import java.util.Map;

public class ThreadLocal {
    private static final Map<String, Object> store = new HashMap<>();
    private ThreadLocal() {}

    /**
     * 문자열로 키값을 지정하면 위험한 상황이 있을 수 있다.
     * @param key - 현 스레드의 값을 키값으로 한다 (문자열로 한다..)
     * @param value
     */
    public static void set(String key, Object value) {
        store.put(key, value);
    }

    public static Object get(String key) {
        return store.get(key);
    }
}
