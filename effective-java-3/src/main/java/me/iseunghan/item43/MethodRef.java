package me.iseunghan.item43;

import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

public class MethodRef {
    public static void main(String[] args) {
        // 메서드 참조를 사용하는 법
        Map<String, String> map = new HashMap<>();
        map.merge("key", "value-", (oldValue, newValue) -> oldValue + newValue);
        map.merge("key", "value-", (oldValue, newValue) -> oldValue.concat(newValue));
        map.merge("key", "value", String::concat);
        assert map.get("key").equals("value-value-value");
        System.out.println("map = " + map);    // value-value-value

        System.out.println("---------------------");
        String argument = "test-argument";

        // 아래 방법 중 뭐가 나은가? 3번째 아닌가..?
        int response = OhMyGoshThisClassNameIsVeryLong.service(argument, OhMyGoshThisClassNameIsVeryLong::action);
        int response2 = OhMyGoshThisClassNameIsVeryLong.service(argument, s -> s.length());
        int response3 = OhMyGoshThisClassNameIsVeryLong.service(argument, String::length);
        assert response == argument.length();
        System.out.println("response = " + response);
        System.out.println("response2 = " + response2);
        System.out.println("response3 = " + response3);
    }

    public static class OhMyGoshThisClassNameIsVeryLong {
        public static int action(String string) {
            return string.length();
        }

        public static int service(String argument, Function<String, Integer> function) {
            return function.apply(argument);
        }
    }
}
