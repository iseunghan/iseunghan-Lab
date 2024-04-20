package book.ch6.sub3;

import org.junit.jupiter.api.Test;

import java.util.*;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class BookSolution {

    @Test
    void test() {
        Solution solution = new Solution();
        String[] result = solution.reorderLogFiles(new String[]{"dig1 8 1 5 1", "let1 art can", "dig2 3 6", "let2 own kit dig", "let3 art zero"});
        assertEquals(Arrays.toString(result), "[let1 art can, let3 art zero, let2 own kit dig, dig1 8 1 5 1, dig2 3 6]");
    }

    static class Solution {
        public String[] reorderLogFiles(String[] logs) {
            List<String> letters = new ArrayList<>(logs.length);
            List<String> digits = new ArrayList<>(logs.length);

            for (String log : logs) {
                if (Character.isDigit(log.split(" ")[1].charAt(0))) {
                    digits.add(log);
                } else {
                    letters.add(log);
                }
            }

            letters.sort((s1, s2) -> {
                String[] s1x = s1.split(" ", 2);
                String[] s2x = s2.split(" ", 2);

                // compareTo는 1: 크다, 0: 같다, -1: 작다 로 응답한다.
                int compared = s1x[1].compareTo(s2x[1]);
                if (compared == 0) {
                    return s1x[0].compareTo(s2x[0]);
                }
                return compared;
            });

            letters.addAll(digits);
            return letters.toArray(new String[0]);
        }

        private boolean isDigitLog(String s) {
            return s.split(" ")[1].charAt(0) < 97;
        }
    }
}
