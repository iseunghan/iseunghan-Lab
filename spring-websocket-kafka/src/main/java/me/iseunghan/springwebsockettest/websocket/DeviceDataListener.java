package me.iseunghan.springwebsockettest.websocket;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class DeviceDataListener {
    private final WebSocketSessionManager sessionManager;

    // 원하는 토픽을 구독해서 특정 세션매니저로 전송
    @KafkaListener(topicPattern = "([0-9A-Za-z]{2}[_]){5}([0-9A-Za-z]{2})", groupId = "device-mac-group")
    public void listen(ConsumerRecord<String, String> record) {
//        log.info("Received message {}: {}", record.topic(), record.value());
        sessionManager.broadcastToSubscribedUsers(record.topic(), record.value());
    }

}
