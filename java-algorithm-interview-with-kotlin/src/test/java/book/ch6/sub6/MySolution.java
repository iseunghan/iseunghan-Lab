package book.ch6.sub6;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class MySolution {

    @Test
    void test() {
        Solution solution = new Solution();
        String result = solution.longestPalindrome("dcbabcdd");
        Assertions.assertEquals(result, "dcbabcd");
    }


    class Solution {
        public String longestPalindrome(String s) {
            int result_x1 = 0;
            int result_x2 = 0;

            // point 2
            for (int i=0; i<= s.length() - 2; i++) {
                int p1 = i;
                int p2 = i + 1;

                do {
                    if (s.charAt(p1) != s.charAt(p2)) break;
                    if ((result_x2 - result_x1) < (p2 - p1)) {
                        result_x1 = p1;
                        result_x2 = p2;
                    }
                } while (--p1 >= 0 && ++p2 <= (s.length() - 1));
            }

            // point 3
            for (int i=0; i<= s.length() - 3; i++) {
                int p1 = i;
                int p2 = i + 2;

                do {
                    if (s.charAt(p1) != s.charAt(p2)) break;
                    if ((result_x2 - result_x1) < (p2 - p1)) {
                        result_x1 = p1;
                        result_x2 = p2;
                    }
                } while (--p1 >= 0 && ++p2 <= (s.length() - 1));
            }

            return s.substring(result_x1, result_x2 + 1);
        }
    }
}
