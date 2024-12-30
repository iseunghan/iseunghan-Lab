package me.iseunghan;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class LambdaExample1Test {

    @Test
    @DisplayName("기존 중복 코드 메서드 호출")
    void asIsTest() {
        LambdaExample1 ex = new LambdaExample1();
        List<Match> matches = List.of(new Match(1, 1), new Match(3, 2));
        int totalHeadersAttempt = ex.getTotalHeadersAttempt(matches);
        int totalMiddleShootAttempt = ex.getTotalMiddleShootAttempt(matches);
        System.out.println("totalHeadersAttempt = " + totalHeadersAttempt);
        System.out.println("totalMiddleShootAttempt = " + totalMiddleShootAttempt);
    }

    @Test
    @DisplayName("중복이 제거된 메서드 호출 (함수형 인터페이스 + 람다)")
    void toBeTest() {
        LambdaExample1 ex = new LambdaExample1();
        List<Match> matches = List.of(new Match(1, 1), new Match(3, 2));
        int totalHeadersAttempt = ex.getTotalHeadersAttemptRefactor(matches);
        int totalMiddleShootAttempt = ex.getTotalMiddleShootAttemptRefactor(matches);
        System.out.println("totalHeadersAttempt = " + totalHeadersAttempt);
        System.out.println("totalMiddleShootAttempt = " + totalMiddleShootAttempt);
    }
}