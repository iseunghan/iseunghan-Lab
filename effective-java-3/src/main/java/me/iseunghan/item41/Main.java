package me.iseunghan.item41;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        asIsTest();
        toBeTest();
    }

    static void asIsTest() {
        LambdaExample1 ex = new LambdaExample1();
        List<Match> matches = List.of(new Match(1, 1), new Match(3, 2));
        int totalHeadersAttempt = ex.getTotalHeadersAttempt(matches);
        int totalMiddleShootAttempt = ex.getTotalMiddleShootAttempt(matches);
        System.out.println("[asIsTest] totalHeadersAttempt = " + totalHeadersAttempt);
        System.out.println("[asIsTest] totalMiddleShootAttempt = " + totalMiddleShootAttempt);
    }

    static void toBeTest() {
        LambdaExample1 ex = new LambdaExample1();
        List<Match> matches = List.of(new Match(1, 1), new Match(3, 2));
        int totalHeadersAttempt = ex.getTotalHeadersAttemptRefactor(matches);
        int totalMiddleShootAttempt = ex.getTotalMiddleShootAttemptRefactor(matches);
        System.out.println("[toBeTest] totalHeadersAttempt = " + totalHeadersAttempt);
        System.out.println("[toBeTest] totalMiddleShootAttempt = " + totalMiddleShootAttempt);
    }
}
