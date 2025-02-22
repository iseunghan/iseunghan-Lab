package me.iseunghan.item78;


import java.util.concurrent.TimeUnit;

public class IsThreadStop {
    private static boolean stopRequested;

    public static void main(String[] args) throws InterruptedException {
        Thread backgroundThread = new Thread(() -> {
            int i = 0;
            while (!stopRequested)
                i++;
        });
        backgroundThread.start();

        TimeUnit.SECONDS.sleep(1);
        stopRequested = true;   // 정말 1초 뒤에 종료될까?
    }
    // 정답은 아니다!
    // 동기화가 없다면? JVM이 컴파일 시점에 아래와 같이 최적화 할 수도 있다.
    // if (!stopRequested)
    //   while (true)
    //     i++;
    // 여전히 프로그램이 끝날 것 같은가?
}
