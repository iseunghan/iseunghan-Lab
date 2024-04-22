package me.iseunghan.item33;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class Favorites {
    private final Map<Class<?>, Object> favorites = new HashMap<>();

    public <T> void putFavorite(Class<T> clazz, T instance) {
        favorites.put(clazz, instance);
        // 타입 불변식을 어기지 않도록하는 안전장치!
        // favorites.put(Objects.requireNonNull(clazz), clazz.cast(instance));
    }

    public <T> T getFavorite(Class<T> clazz) {
        return clazz.cast(favorites.get(clazz));
    }
}
