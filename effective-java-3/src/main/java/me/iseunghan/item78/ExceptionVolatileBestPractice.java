package me.iseunghan.item78;


import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class ExceptionVolatileBestPractice {
    // volatile은 무조건 main memory에서 마지막 상태를 읽어온다. synchronized의 효과를 불러오면서 더 빠르게 작동한다.
    private static volatile int nextSerialNumber = 0;
    private static AtomicInteger nextSerialNumber2 = new AtomicInteger(0);

    public static int getNextSerialNumber() {
        return nextSerialNumber++;
    }

    public static void main(String[] args) throws InterruptedException {
        Thread backgroundThread = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println(Thread.currentThread().getName() + " -> " + getNextSerialNumber());
            }
        });
        Thread backgroundThread2 = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println(Thread.currentThread().getName() + " -> " + getNextSerialNumber());
            }
        });
//        backgroundThread.start();
//        backgroundThread2.start();
        //Thread-0 -> 0
        //Thread-0 -> 2
        //Thread-1 -> 1
        //Thread-0 -> 3
        //Thread-1 -> 4
        //Thread-0 -> 5
        //Thread-1 -> 6
        //Thread-0 -> 7
        //Thread-1 -> 8
        //Thread-1 -> 9

        Thread backgroundThread3 = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println(Thread.currentThread().getName() + " -> " + nextSerialNumber2.getAndIncrement());
            }
        });
        Thread backgroundThread4 = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println(Thread.currentThread().getName() + " -> " + nextSerialNumber2.getAndIncrement());
            }
        });
        backgroundThread3.start();
        backgroundThread4.start();
        //Thread-3 -> 1
        //Thread-2 -> 0
        //Thread-3 -> 2
        //Thread-3 -> 4
        //Thread-2 -> 3
        //Thread-3 -> 5
        //Thread-2 -> 6
        //Thread-3 -> 7
        //Thread-2 -> 8
        //Thread-2 -> 9
    }
}
