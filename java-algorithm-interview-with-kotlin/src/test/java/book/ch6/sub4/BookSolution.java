package book.ch6.sub4;

import java.util.*;
import java.util.stream.Collectors;

public class BookSolution {


    public String mostCommonWord(String paragraph, String[] banned) {
        final Set<String> ban = new HashSet<>(Arrays.asList(banned));
        final Map<String, Integer> counts = new HashMap<>();
        final List<String> parsedStringList = Arrays.stream(paragraph.replaceAll("\\W+", " ").split(" "))
                .map(String::toLowerCase)
                .filter(s -> !ban.contains(s))
                .collect(Collectors.toList());

        parsedStringList.forEach(s -> {
                    counts.put(s, counts.getOrDefault(s, 0) + 1);
                });
        return Collections.max(counts.entrySet(), Map.Entry.comparingByValue()).getKey();
    }
}
