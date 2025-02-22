package me.iseunghan.item73;

public class BestPracticeException {
    public static void main(String[] args) throws HigherLevelException {
        translate_exception();
        /**
         * 발생한 예외
         * Exception in thread "main" me.iseunghan.item73.HigherLevelException: higher level exception
         * 	at me.iseunghan.item73.BestPracticeException.translate_exception(BestPracticeException.java:13)
         * 	at me.iseunghan.item73.BestPracticeException.main(BestPracticeException.java:5)
         *
         * Execution failed for task ':me.iseunghan.item73.BestPracticeException.main()'.
         * > Process 'command '/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/java'' finished with non-zero exit value 1
         */

        chain_exception();
        /**
         * 발생한 예외 (좀 더 자세하게 나온다. 근본 원인까지 출력된다.)
         * Exception in thread "main" me.iseunghan.item73.HigherLevelException: lower level exception
         * 	at me.iseunghan.item73.BestPracticeException.chain_exception(BestPracticeException.java:37)
         * 	at me.iseunghan.item73.BestPracticeException.main(BestPracticeException.java:16)
         * Caused by: me.iseunghan.item73.LowerLevelException: lower level exception
         * 	at me.iseunghan.item73.BestPracticeException.run(BestPracticeException.java:29)
         * 	at me.iseunghan.item73.BestPracticeException.chain_exception(BestPracticeException.java:35)
         * 	... 1 more
         *
         * Caused by: me.iseunghan.item73.LowerLevelException: lower level exception
         *
         * Execution failed for task ':me.iseunghan.item73.BestPracticeException.main()'.
         * > Process 'command '/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/java'' finished with non-zero exit value 1
         */
    }
    // 상위 계층에서는 저수준 예외를 잡아 자신의 추상화 수준에 맞는 예외로 바꿔 던져야 한다.
    static void translate_exception() throws HigherLevelException {
        try {
            run();
        } catch (LowerLevelException e) {
            throw new HigherLevelException();
        }
    }

    static void run() throws LowerLevelException {
        // do-something
        throw new LowerLevelException();
    }

    // 예외 연쇄: 근본 원인인 저수준 예외를 고수준 예외에 실어 보내는 방식. 별도 접근자 메서드 getCause를 통해 저수준 예외를 꺼내볼 수 있다.
    static void chain_exception() throws HigherLevelException {
        try {
            run();
        } catch (LowerLevelException e) {
            throw new HigherLevelException(e.getMessage(), e);
        }
    }

}
