package me.iseunghan.item37;

import java.util.EnumMap;
import java.util.Map;
import java.util.stream.Stream;

import static java.util.stream.Collectors.groupingBy;
import static java.util.stream.Collectors.toMap;

public enum BestPractice_Phase {
    SOLID, LIQUID, GAS;

    public enum Transition {
        MELT(SOLID, LIQUID), FREEZE(LIQUID, SOLID), BOIL(LIQUID, GAS), CONDENSE(GAS, LIQUID), SUBLIME(SOLID, GAS), DEPOSIT(GAS, LIQUID);

        private final BestPractice_Phase from;
        private final BestPractice_Phase to;

        Transition(BestPractice_Phase from, BestPractice_Phase to) {
            this.from = from;
            this.to = to;
        }

        private static final Map<BestPractice_Phase, Map<BestPractice_Phase, Transition>> m = Stream.of(values())
                .collect(groupingBy(
                                t -> t.from,
                                () -> new EnumMap<>(BestPractice_Phase.class),
                                toMap(t -> t.to, t -> t, (x, y) -> y, () -> new EnumMap<>(BestPractice_Phase.class))
                        )
                );

        public static Transition from(BestPractice_Phase from, BestPractice_Phase to) {
            return m.get(from).get(to);
        }
    }
}
