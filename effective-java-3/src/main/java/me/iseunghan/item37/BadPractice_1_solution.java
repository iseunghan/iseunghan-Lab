package me.iseunghan.item37;

import java.util.*;

public class BadPractice_1_solution {
    public static void main(String[] args) {
        Map<Plant.LifeCycle, Set<Plant>> plantsByLifeCycle = new EnumMap<>(Plant.LifeCycle.class);

        List<Plant> garden = List.of(
                new Plant("p1", Plant.LifeCycle.ANNUAL),
                new Plant("p2", Plant.LifeCycle.BIENNIAL),
                new Plant("p3", Plant.LifeCycle.PERENNIAL)
        );
        for (Plant.LifeCycle lc : Plant.LifeCycle.values()) {
            plantsByLifeCycle.put(lc, new HashSet<>()); // *기존 ordinal과는 확연하게 달라서 변경에도 유연하다.
        }
        for (Plant p : garden) {
            plantsByLifeCycle.get(p.lifeCycle).add(p);
        }
        System.out.println(plantsByLifeCycle);
    }
}
