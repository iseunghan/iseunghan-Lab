package book.ch6.sub6;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class BookSolution {

    @Test
    void test() {
        Solution solution = new Solution();
        String result = solution.longestPalindrome("dcbabcdd");
        Assertions.assertEquals(result, "dcbabcd");
    }


    class Solution {
        int left, maxLen;

        public String longestPalindrome(String s) {
            int len = s.length();
            if (len < 2) return s;

            for (int i = 0; i < len - 1; i++) {
                extendPalindrome(s, i, i + 1);
                extendPalindrome(s, i, i + 2);
            }
            return s.substring(left, left + maxLen);
        }

        private void extendPalindrome(String s, int j, int k) {
            while (j >= 0 && k < s.length() && s.charAt(j) == s.charAt(k)) {
                j--;
                k++;
            }

            if (maxLen < k - j - 1) {
                left = j + 1;
                maxLen = k - j - 1;
            }
        }
    }
}
