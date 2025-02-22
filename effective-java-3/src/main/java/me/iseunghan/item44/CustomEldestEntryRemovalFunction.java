package me.iseunghan.item44;

import java.util.Map;

/**
 * boolean LinkedHashMap.removeEldestEntry 함수를 사용하면 캐시를 구현할 수 있다.
 * 하지만 람다가 존재하는 지금 다시 만든다면 아래와 같이 만들었을 것이다.
 */
@FunctionalInterface
public interface CustomEldestEntryRemovalFunction<K, V> {
    boolean remove(Map<K, V> map, Map.Entry<K, V> eldest);  // 매개변수는 기존 맵과 삭제할 오래된 원소를 건내서 캐시 용량을 지킬 수 있다.
}
