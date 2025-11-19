package me.iseunghan.springwebsockettest.websocket;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.util.Arrays;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Deprecated
public class WebSocketSessionManager {
    private final Map<String, WebSocketSession> userSessions = new ConcurrentHashMap<>();
    private final Map<String, Set<String>> userDeviceSubscriptions = new ConcurrentHashMap<>();
    private final static String DELIMITER = "-";
    private final ObjectMapper mapper = new ObjectMapper();

    public void updateSubscription(String userId, String message) {
        Set<String> subscription = userDeviceSubscriptions.computeIfAbsent(userId, k -> ConcurrentHashMap.newKeySet());
        subscription.clear();
        Arrays.stream((message.startsWith("[") && message.endsWith("]")
                        ? message.substring(1, message.length() - 1)
                        : message).split(","))
                .map(String::trim)
                .forEach(subscription::add);
        log.info(">> [subscription]: {}", message);
    }

    public Set<String> getSubscriptions(String userId) {
        return userDeviceSubscriptions.getOrDefault(userId, ConcurrentHashMap.newKeySet());
    }

    public void broadcastToSubscribedUsers(String topic, String message) {
        String[] split = topic.split(DELIMITER);
        if (split.length != 5) {
            log.warn("Invalid topic format: {}", topic);
            return;
        }
        ObjectNode result = mapper.createObjectNode();
        String deviceId = split[3], postfix = split[4];
        try {
            result.set(postfix, mapper.readTree(message));
        } catch (JsonProcessingException e) {
            return;
        }

        userDeviceSubscriptions.forEach((userId, subscriptions) -> {
            if (subscriptions.contains(deviceId)) {
                WebSocketSession session = userSessions.get(userId);
                if (session != null && session.isOpen()) {
                    try {
                        session.sendMessage(new TextMessage(result.toString()));
                    } catch (IOException e) {
                        log.error(e.getMessage(), e);
                    }
                }
            }
        });
    }

    public void registerSession(WebSocketSession session) {
        userSessions.put(session.getId(), session);
    }

    public void unRegisterSession(WebSocketSession session) {
        userSessions.remove(session.getId(), session);
    }
}
