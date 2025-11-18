package me.iseunghan.springwebsockettest.websocket;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class DeviceDataListener {
    private final ObjectMapper mapper;
    private final static String DELIMITER = "-";
    private final SimpMessagingTemplate messagingTemplate;

    // 원하는 토픽을 구독해서 특정 세션매니저로 전송
    @KafkaListener(topicPattern = "^([A-Za-z0-9]+)-([0-9]+)-([0-9]+)-([0-9A-Za-z]{2}[_]){5}([0-9A-Za-z]{2})-([A-Za-z0-9_-]+)$", groupId = "device-mac-group")
    public void listen(ConsumerRecord<String, String> record) {
//        log.info("Received message {}: {}", record.topic(), record.value());
        String[] split = record.topic().split(DELIMITER);

        if (split.length != 5) {
            log.warn("Invalid topic format: {}", record.topic());
            return;
        }
        ObjectNode result = mapper.createObjectNode();
        String deviceId = split[3], postfix = split[4];
        try {
            result.set(postfix, mapper.readTree(record.value()));
        } catch (JsonProcessingException e) {
            return;
        }

        String destination = "/come-out/" + deviceId;
        messagingTemplate.convertAndSend(destination, result.toString());
    }

}
