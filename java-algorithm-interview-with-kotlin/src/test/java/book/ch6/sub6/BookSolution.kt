package book.ch6.sub6

import org.junit.jupiter.api.Test

class BookSolution {

    class Solution {
        var left: Int = 0
        var maxLen: Int = 0

        fun extendPalindrome(s: String, j: Int, k: Int) {
            // 코틀린은 파라미터(value-parameter) 수정 불가
            var l = j
            var r = k

            while (l >= 0 && r < s.length && s[l] == s[r]) {
                l--
                r++
            }

            if (maxLen < r - l - 1) {
                left = l + 1
                maxLen = r - l - 1
            }
        }

        fun longestPalindrome(s: String): String? {
            val len = s.length

            if (len < 2) return s

            for (i in 0 until len - 1) {
                extendPalindrome(s, i, i + 1)
                extendPalindrome(s, i, i + 2)
            }
            return s.substring(left, left + maxLen)
        }
    }
}