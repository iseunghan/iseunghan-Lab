package me.iseunghan

fun main() {
    변수는_가변_불변으로_선언할수있다()
    널을허용할수있다()
    타입추론기능()
}

fun 변수는_가변_불변으로_선언할수있다() {
    // 변수는 var(가변), val(불변)로 선언할 수 있다.
    var i: Int = 10
    val j: Int = 10

    i = 20
//    j = 20 // val은 재 할당 불가!

    println(i)  //20
    println(j)  //10
}

fun 널을허용할수있다() {
    // ?를 통해 nullable하게 만들 수 있다.
    var i1: Int = 10
    var i2: Int? = 10

//    i1 = null // compile error!
    i2 = null

    println(i1) // 10
    println(i2) //null

    // string 타입도 마찬가지
    var s1: String = "ABC"
    var s2: String? = "ABC"

//    i1 = null // compile error!
    s2 = null

    println(s1) // ABC
    println(s2) // null
}

fun 타입추론기능() {
    // type 추론 기능
    val s = "ABC"
    val i = 1
    val l = 1L
    val d = 1.0
    val f = 1.0f

    println("s= " + s::class)   // s= class java.lang.String (Kotlin reflection is not available)
    println("i= " + i::class)   // i= int (Kotlin reflection is not available)
    println("l= " + l::class)   // l= long (Kotlin reflection is not available)
    println("d= " + d::class)   // d= double (Kotlin reflection is not available)
    println("f= " + f::class)   // f= float (Kotlin reflection is not available)
}
