package me.iseunghan.springtest.controller.advice;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.NoHandlerFoundException;

import java.util.Map;

import static org.springframework.http.HttpStatus.NOT_FOUND;

@RestControllerAdvice
public class GlobalControllerAdvice {

    @ExceptionHandler(NoHandlerFoundException.class)
    public ResponseEntity<Map<String, String>> noHandlerFoundHandle(NoHandlerFoundException e) {
        return ResponseEntity.status(NOT_FOUND)
                .body(Map.of(
                        "statusCode", "404",
                        "message", "존재하지 않는 API 입니다."
                ));
    }
}
