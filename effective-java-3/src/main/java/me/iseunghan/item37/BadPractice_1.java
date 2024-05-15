package me.iseunghan.item37;

import java.lang.management.PlatformLoggingMXBean;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class BadPractice_1 {
    public static void main(String[] args) {
        Set<Plant>[] plantsByLifeCycle = (Set<Plant>[]) new Set[Plant.LifeCycle.values().length];
        for (int i = 0; i < plantsByLifeCycle.length; i++) {
            plantsByLifeCycle[i] = new HashSet<>();
        }

        List<Plant> garden = List.of(
                new Plant("p1", Plant.LifeCycle.ANNUAL),
                new Plant("p2", Plant.LifeCycle.BIENNIAL),
                new Plant("p3", Plant.LifeCycle.PERENNIAL)
        );
        for (Plant p : garden) {
            plantsByLifeCycle[p.lifeCycle.ordinal()].add(p);    // *만약 LifeCycle 중간에 데이터가 추가된다면? ordinal 일관성을 보장할 수 있는가?
        }

        for (int i = 0; i < plantsByLifeCycle.length; i++) {
            System.out.printf("%s: %s%n", Plant.LifeCycle.values()[i], plantsByLifeCycle[i]);
        }
    }
}
