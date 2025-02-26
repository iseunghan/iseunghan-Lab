package me.iseunghan

fun main() {
    대소문자_비교() // a < b
    null체크()    // null check!
    배열에_존재하는지_체크()  // contains!
    when_case_switch()  // price is 300"
    when_case_switch_range()    // price is 300..399
}

fun when_case_switch() {
    val price: Int = 300

    when (price) {
        100 -> println("price is 100")
        200 -> println("price is 200")
        300 -> println("price is 300")
        else -> println("price is neutral")
    }
}

fun when_case_switch_range() {
    val price: Int = 301

    when (price) {
        in 100..101 -> println("price is 100..199")
        in 200..299 -> println("price is 200..299")
        in 300..399 -> println("price is 300..399")
        else -> println("price is neutral")
    }
}

fun 배열에_존재하는지_체크() {
    val price: Int = 100

    if (price in arrayOf(100, 200, 300)) {
        println("contains!")
    } else {
        println("not contains!")
    }
}

fun 대소문자_비교() {
    val a: Int = 100
    val b: Int = 200

    if (a > b) {
        println("a > b")
    } else {
        println("a < b")
    }
}

fun null체크() {
    val a: Int? = null

    if (a == null) {
        println("null check!")
    } else {
        println("a = ${a}")
    }
}