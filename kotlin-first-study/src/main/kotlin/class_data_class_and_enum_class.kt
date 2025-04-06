package me.iseunghan

fun main() {
    val tempClass = TempClass("name", 1)
    println(tempClass)  //me.iseunghan.TempClass@2d209079

    val immuDataClass = TempImmutableDataClass("immutable", 1)
//     cannot mutable errors!
//    immuDataClass.name = "mutable2"
//    immuDataClass.cnt = 2
    println(immuDataClass)  //TempImmutableDataClass(name=immutable, cnt=1)

    val muDataClass = TempMutableDataClass("mutable", 1)
    muDataClass.name = "mutable2"
    muDataClass.cnt = 2
    println(muDataClass)    //TempMutableDataClass(name=mutable2, cnt=2)

    println("color: ${Color.RED.name}, ordinary: ${Color.RED.ordinal}") //color: RED, ordinary: 0
}

class TempClass (
    val name: String,
    val cnt: Int
)

// data class는 기본적으로 getter, setter, toString, hashCode, equals를 생성 (Lombok @Data 어노테이션)
data class TempImmutableDataClass(
    val name: String,
    val cnt: Int
)

// var가 있으면 자동으로 Setter까지 생성!
data class TempMutableDataClass(
    var name: String,
    var cnt: Int
)

enum class Color {
    RED, GREEN, BLUE, YELLOW
}