package me.iseunghan.springembeddedkafkatest.common

import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Service

@Service
class KafkaConsumer {

    @KafkaListener(topics = ["\${spring.kafka.template.default-topic}"], groupId = "\${spring.kafka.consumer.group-id}")
    fun poll(msg: String) {
        println(">> $msg")
    }
}