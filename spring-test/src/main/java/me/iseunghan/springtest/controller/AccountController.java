package me.iseunghan.springtest.controller;

import jakarta.validation.Valid;
import me.iseunghan.springtest.dto.CreateAccountDto;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AccountController {

    @PostMapping("/accounts")
    public String createUser(@Valid @RequestBody CreateAccountDto createAccountDto) {
        // 저장 로직
        return "사용자가 정상적으로 생성 되었습니다.";
    }
}
