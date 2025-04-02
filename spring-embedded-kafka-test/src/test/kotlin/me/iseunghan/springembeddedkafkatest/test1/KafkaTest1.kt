package me.iseunghan.springembeddedkafkatest.test1

import org.junit.jupiter.api.Test
import org.springframework.boot.test.context.SpringBootTest

@SpringBootTest
class KafkaTest1 {

	@Test
	fun contextLoads() {
		// This test will occur UnknownHostException

		// java.net.UnknownHostException: logs-service-kafka-1: nodename nor servname provided, or not known
		// ...
	}

}
