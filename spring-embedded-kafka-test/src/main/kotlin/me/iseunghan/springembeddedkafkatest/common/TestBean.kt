package me.iseunghan.springembeddedkafkatest.common

import org.springframework.stereotype.Component

@Component
class TestBean {

    fun test() {
        println("testBean")
    }
}