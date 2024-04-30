package book.ch6.sub5

import org.junit.jupiter.api.Test

class BookSolution {
    @Test
    fun test() {
        val answer = groupAnagrams(arrayOf("eat", "tea", "tan", "ate", "nat", "bat"))
        println(answer)
    }

    fun groupAnagrams(strs: Array<String>): List<List<String>> {
        val results: MutableMap<String, MutableList<String>> = mutableMapOf()

        for (s in strs) {
            val key = s.toCharArray().sorted().joinToString("")
            results.getOrPut(key) { mutableListOf() }
            results[key]!!.add(s)
        }
        return ArrayList<List<String>>(results.values)
    }
}