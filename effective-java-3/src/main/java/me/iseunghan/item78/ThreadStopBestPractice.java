package me.iseunghan.item78;


import java.util.concurrent.TimeUnit;

public class ThreadStopBestPractice {
    // volatile은 무조건 main memory에서 마지막 상태를 읽어온다. synchronized의 효과를 불러오면서 더 빠르게 작동한다.
    private static volatile boolean stopRequested;

    public static void main(String[] args) throws InterruptedException {
        Thread backgroundThread = new Thread(() -> {
            int i = 0;
            while (!stopRequested)
                i++;
        });
        backgroundThread.start();

        TimeUnit.SECONDS.sleep(1);
        stopRequested = true;  // 동기화와 함께라면 정상적으로 종료된다!
    }
}
