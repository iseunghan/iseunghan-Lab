package me.iseunghan.springembeddedkafkatest.test2

import me.iseunghan.springembeddedkafkatest.common.TestBean
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.kafka.test.context.EmbeddedKafka
import kotlin.test.Test

@EmbeddedKafka(partitions = 1, topics = ["\${spring.kafka.template.default-topic}", "topic1"])
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class KafkaTest2(
    @Autowired val kafkaTemplate: KafkaTemplate<String, String>,
    @Autowired val testBean: TestBean
) {
    @Value("\${spring.kafka.template.default-topic}")
    lateinit var topic: String

    @Test
    fun isSucceed() {
        testBean.test()
        kafkaTemplate.send(topic, "message2")
        println("isSucceed2")
    }
}