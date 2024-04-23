package book.ch6.sub4;

import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MySolution {

    @Test
    void mySoulution() {
//        String paragraph = "Bob hit a ball, the hit BALL flew far after it was hit.";
//        String[] banned = {"hit"};
        String paragraph = "a, a, a, a, b,b,b,c c";
        String[] banned = {"a"};
        String output = "ball";

        String resultString = "";
        long maxCount = 0L;

        final List<String> parsedStringList = Arrays.stream(paragraph.split(" "))
                .map(s -> s.replace(".", ""))
                .map(s -> s.replace(",", ""))
                .map(s -> s.replace(";", ""))
                .map(s -> s.replace("?", ""))
                .map(s -> s.replace("!", ""))
                .map(String::toLowerCase)
                .filter(s -> {
                    for (String str : banned) {
                        if (str.equals(s))  return false;
                    }
                    return true;
                })
                .collect(Collectors.toList());

        Set<String> distinctString = new HashSet<>(parsedStringList.size());

        for (int i=0; i<parsedStringList.size(); i++) {
            if (distinctString.contains(parsedStringList.get(i)))
                continue;
            distinctString.add(parsedStringList.get(i));

            int count = 1;
            for (int j = i+1; j < parsedStringList.size(); j++) {
                if (parsedStringList.get(i).equals(parsedStringList.get(j))) {
                    count++;
                }
            }

            if (count > maxCount) {
                maxCount = count;
                resultString = parsedStringList.get(i);
            }
        }
        assertEquals(output, resultString);
    }
}
