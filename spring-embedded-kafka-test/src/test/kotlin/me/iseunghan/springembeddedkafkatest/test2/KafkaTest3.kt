package me.iseunghan.springembeddedkafkatest.test2

import me.iseunghan.springembeddedkafkatest.common.TestBean2
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.kafka.test.context.EmbeddedKafka
import org.springframework.test.context.ActiveProfiles
import kotlin.test.Test

@ActiveProfiles("test")
@EmbeddedKafka(partitions = 1, topics = ["\${spring.kafka.template.default-topic}", "topic2"], brokerProperties = ["listeners=PLAINTEXT://localhost:0", "port=0"])
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class KafkaTest3(
    @Autowired val kafkaTemplate: KafkaTemplate<String, String>,
    @Autowired val testBean: TestBean2
) {
    @Value("\${spring.kafka.template.default-topic}")
    lateinit var topic: String

    @Test
    fun isSucceed() {
        testBean.test()
        kafkaTemplate.send(topic, "message3")
        println("isSucceed3")
    }
}