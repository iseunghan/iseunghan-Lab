package me.iseunghan.item33;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

public class Main {
    public static void main(String[] args) {
        Favorites f = new Favorites();

        f.putFavorite(String.class, "Cafe");
        f.putFavorite(Integer.class, 0xcafebabe);
        f.putFavorite(Class.class, Favorites.class);

        String fString = f.getFavorite(String.class);
        int fInteger = f.getFavorite(Integer.class);
        var fClass = f.getFavorite(Class.class);

        System.out.printf("%s %x %s%n", fString, fInteger, fClass.getName());

        Set<Integer> integers = new HashSet<>();
        ((HashSet)integers).add("문자열입니다.");

    }
}
