package me.iseunghan.item63;

import java.util.function.Consumer;

public class StringFaster {
    public static void main(String[] args) {
        run(StringFaster::statement);
        run(StringFaster::statement2);
    }

    static String[] makeDummy() {
        String[] numItems = new String[1000];
        for (int i = 0; i < numItems.length; i++) {
            numItems[i] = "Example String " + (i + 1);
        }
        return numItems;
    }

    static void run(Consumer<String[]> function) {
        String[] args = makeDummy();

        long start = System.currentTimeMillis();
        function.accept(args);
        System.out.println(System.currentTimeMillis() - start);
    }

    static void statement(String[] numItems) {
        String answer = "";
        for (int i = 0; i < numItems.length; i++) {
            answer += numItems[i];
        }
//        System.out.println(answer);
    }

    static void statement2(String[] numItems) {
        StringBuilder answer = new StringBuilder(numItems.length * 20); // capacity를 잘못잡으면 1ms가 소요되는 반면, 넉넉하게 잡으면 0ms가 소요된다..ㅋㅋ
        for (int i = 0; i < numItems.length; i++) {
            answer.append(numItems[i]);
        }
//        System.out.println(answer);
    }
}
