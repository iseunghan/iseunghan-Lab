package book.ch6.sub3

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BookSolution_kotlin {

    @Test
    fun test() {
        val result = reorderLogFiles(arrayOf("dig1 8 1 5 1", "let1 art can", "dig2 3 6", "let2 own kit dig", "let3 art zero"))
        Assertions.assertEquals(result.joinToString(), arrayOf("let1 art can","let3 art zero","let2 own kit dig","dig1 8 1 5 1","dig2 3 6").joinToString())
    }

    fun reorderLogFiles(logs: Array<String>): Array<String> {
        val letters = mutableListOf<String>()
        val digits = mutableListOf<String>()

        for (log in logs) {
            if (Character.isDigit(log.split(" ")[1][0])) {
                digits.add(log)
            } else {
                letters.add(log)
            }
        }

        letters.sortWith(Comparator { s1, s2 ->
            val s1x = s1.split(" ", limit = 2)
            val s2x = s2.split(" ", limit = 2)

            val compared = s1x[1].compareTo(s2x[1])
            if (compared == 0) {
                s1x[0].compareTo(s2x[0])
            } else {
                compared
            }
        })

        letters.addAll(digits)
        return letters.toTypedArray()
    }

}
