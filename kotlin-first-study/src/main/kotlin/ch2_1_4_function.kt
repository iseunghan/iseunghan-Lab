package me.iseunghan

fun main() {
    val price1: Int = 13
    val price2: Int = 7

    println(sum(a = price1, b = price2))    // 20
    println(sum_compressed(a = price1, b = price2)) // 20
}

fun sum(a: Int, b: Int): Int {
    return a + b
}

// 함수를 변수처럼 선언할 수 있다!
fun sum_compressed(a: Int, b: Int) = a + b