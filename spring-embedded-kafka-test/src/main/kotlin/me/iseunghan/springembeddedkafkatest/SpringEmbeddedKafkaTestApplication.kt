package me.iseunghan.springembeddedkafkatest

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class SpringEmbeddedKafkaTestApplication

fun main(args: Array<String>) {
	runApplication<SpringEmbeddedKafkaTestApplication>(*args)
}
