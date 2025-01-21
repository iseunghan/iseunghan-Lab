package me.iseunghan.springwebsockettest.websocket;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.util.StringUtils;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

/**
 * 범용적으로 사용되는 웹소켓핸들러. 세션을 등록,해제, 메시지를 전송하는 역할을 한다. 이 핸들러는 어떤 메시지가 전송되는지 알 필요가 없어야 한다.
 */
@Slf4j
@RequiredArgsConstructor
public class WebsocketHandler extends TextWebSocketHandler {
    private final WebSocketSessionManager sessionManager;

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        log.info(">>> [register]: {}", session.getId());
        sessionManager.registerSession(session);
    }

    @Override
    public void handleMessage(WebSocketSession session, WebSocketMessage<?> message) throws Exception {
        if (message instanceof TextMessage textMessage) {
            String payload = textMessage.getPayload();
            if (StringUtils.hasText(payload)) {
                sessionManager.updateSubscription(session.getId(), payload);
            }
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        log.info(">>> [unregister]: {}", session.getId());
        sessionManager.unRegisterSession(session);
    }
}
