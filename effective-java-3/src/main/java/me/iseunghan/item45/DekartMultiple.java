package me.iseunghan.item45;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class DekartMultiple {
    public static class Card {
        private final Suit suit;
        private final Rank rank;

        Card(Suit suit, Rank rank) {
            this.suit = suit;
            this.rank = rank;
        }
    }

    public enum Suit {}
    public enum Rank {}

    /**
     * standard_newDeck() 함수와 stream_newDeck() 함수 중 어느 것이 마음에 드는가?
     * 물론 정답은 없다. 둘 중 마음에 드는 함수를 골라 사용하면 된다.
     */
    private static List<Card> standard_newDeck() {
        List<Card> result = new ArrayList<>();
        for (Suit suit : Suit.values())
            for (Rank rank : Rank.values())
                result.add(new Card(suit, rank));
        return result;
    }

    private static List<Card> stream_newDeck() {
//        return Arrays.stream(Suit.values()) // <-- 대신 사용해도 문제는 없다.
        return Stream.of(Suit.values())
                .flatMap(suit -> Stream.of(Rank.values()).map(rank -> new Card(suit, rank)))
                .collect(Collectors.toList());
    }
}
