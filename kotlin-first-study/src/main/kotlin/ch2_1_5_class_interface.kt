package me.iseunghan

fun main() {
    val item: Item = Item("book", 10000)
    println("item = ${item.name}, price = ${item.price}") // item = book, price = 10000
    item.buy()
    item.sell()
}

class Item(
    val name: String,
    val price: Int
) : ItemTrade {
    override fun buy() {
        println("buy: $name, $price")
    }

    override fun sell() {
        println("sell: $name, $price")
    }

}

interface ItemTrade {
    fun buy()
    fun sell()
}