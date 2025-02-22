package me.iseunghan.item79;

import java.util.HashSet;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class Main {
    public static void main(String[] args) {
//        normal_execute();                 // 정상 작동
//        concurrentModification_execute(); // concurrentModificationException 발생
//        dead_lock_execute();              // 교착상태
//        is_dead_lock_free();              // 정상 작동!
        is_dead_lock_free_copyOnWriteArrayList();// 정상 작동!
    }

    public static void normal_execute() {
        ObservableSet<Integer> set = new ObservableSet<>(new HashSet<>());

        set.addObserver((set1, element) -> System.out.println("observer watched: " + element));

        for (int i = 0; i < 10; i++) {
            set.add(i);
        }
    }

    /**
     * 정확히 5에서 동시 수정 예외가 발생한다. (동기화를 열어 확인하고 있는 로직중 누군가 해당 리스트를 수정하려하니 ConcurrentModificationException이 발생한 것 이다)
     * observer watched: 0
     * observer watched: 1
     * observer watched: 2
     * observer watched: 3
     * observer watched: 4
     * observer watched: 5
     * Exception in thread "main" java.util.ConcurrentModificationException
     * at java.base/java.util.ArrayList$Itr.checkForComodification(ArrayList.java:1013)
     * at java.base/java.util.ArrayList$Itr.next(ArrayList.java:967)
     * at me.iseunghan.item79.ObservableSet.notifyElementAdded(ObservableSet.java:29)
     * at me.iseunghan.item79.ObservableSet.add(ObservableSet.java:39)
     * at me.iseunghan.item79.Main.dead_lock_execute(Main.java:35)
     * at me.iseunghan.item79.Main.main(Main.java:8)
     */
    public static void concurrentModification_execute() {
        ObservableSet<Integer> set = new ObservableSet<>(new HashSet<>());

        set.addObserver(new SetObserver<>() {
            @Override
            public void added(ObservableSet<Integer> set, Integer element) {
                System.out.println("observer watched: " + element);
                if (element == 5) {
                    set.removeObserver(this);
                }
            }
        });

        for (int i = 0; i < 10; i++) {
            set.add(i);
        }
    }

    /**
     * 내 컴퓨터에서는 1분이 넘어가도록 끝나지 않아서 강제로 종료시켰다.
     * 이게 바로 교착상태에 빠졌다고 한다.
     * ObservableSet 내부에서 notifyElementAdded 내부에서 synchronized를 통해 Lock을 획득하여 순회하는 도중,
     * 서브 스레드에서 removeObserver 함수 내부에서 synchronized를 통해 Lock을 얻으려 시도하는데 먼저 획득한 main 스레드를 계속 기다리고
     * main 스레드는 그런 서브 스레드를 기다리니 서로 무한정 기다리다 결국 교착상태에 빠지게 된다.
     */
    public static void dead_lock_execute() {
        ObservableSet<Integer> set = new ObservableSet<>(new HashSet<>());

        set.addObserver(new SetObserver<>() {
            @Override
            public void added(ObservableSet<Integer> set, Integer element) {
                System.out.println("observer watched: " + element);

                if (element == 5) {
                    ExecutorService executor = Executors.newSingleThreadExecutor();
                    try {
                        executor.submit(() -> set.removeObserver(this)).get();
                    } catch (ExecutionException | InterruptedException e) {
                        throw new AssertionError(e);
                    } finally {
                        executor.shutdown();
                    }
                }
            }
        });

        for (int i = 0; i < 10; i++) {
            set.add(i);
        }
    }

    public static void is_dead_lock_free() {
        ObservableSet<Integer> set = new ObservableSet_Enhanced<>(new HashSet<>());

        set.addObserver(new SetObserver<>() {
            @Override
            public void added(ObservableSet<Integer> set, Integer element) {
                System.out.println("observer watched: " + element);

                if (element == 5) {
                    ExecutorService executor = Executors.newSingleThreadExecutor();
                    try {
                        executor.submit(() -> set.removeObserver(this)).get();
                    } catch (ExecutionException | InterruptedException e) {
                        throw new AssertionError(e);
                    } finally {
                        executor.shutdown();
                    }
                }
            }
        });

        for (int i = 0; i < 10; i++) {
            set.add(i);
        }
    }

    public static void is_dead_lock_free_copyOnWriteArrayList() {
        ObservableSet<Integer> set = new ObservableSet_without_synchronized<>(new HashSet<>());

        set.addObserver(new SetObserver<>() {
            @Override
            public void added(ObservableSet<Integer> set, Integer element) {
                System.out.println("observer watched: " + element);

                if (element == 5) {
                    ExecutorService executor = Executors.newSingleThreadExecutor();
                    try {
                        executor.submit(() -> set.removeObserver(this)).get();
                    } catch (ExecutionException | InterruptedException e) {
                        throw new AssertionError(e);
                    } finally {
                        executor.shutdown();
                    }
                }
            }
        });

        for (int i = 0; i < 10; i++) {
            set.add(i);
        }
    }
}
