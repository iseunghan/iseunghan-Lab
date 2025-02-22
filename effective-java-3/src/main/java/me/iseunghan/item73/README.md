# 예외를 처리하는 방법 세가지
## 1. 예외 번역
저수준의 예외를 잡아 고수준의 예외로 변환하거나, 좀 더 의미가 통하는 예외(ex. customExceptionClass)로 발생시켜 변역하는 것을 의미
```java
static void run() throws LowerLevelException {
    // do-something
    throw new LowerLevelException();
}

static void translate_exception() throws HigherLevelException {
    try {
        run();
    } catch (LowerLevelException e) {
        throw new HigherLevelException();   // 이런 것을 예외 번역이라 한다!
    }
}
```
예외 발생 시, 로그
```log
Exception in thread "main" me.iseunghan.item73.HigherLevelException: higher level exception
	at me.iseunghan.item73.BestPracticeException.translate_exception(BestPracticeException.java:13)
	at me.iseunghan.item73.BestPracticeException.main(BestPracticeException.java:5)
Execution failed for task ':me.iseunghan.item73.BestPracticeException.main()'.
> Process 'command '/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/java'' finished with non-zero exit value 1
```

## 2. 예외 연쇄
저수준의 예외를 잡아 그저 변역하는 것이 아닌, 근본 원인(cause)인 저수준 예외를 고수준 예외에 실어 보내는 방식. 별도 접근자 메서드 getCause를 통해 저수준 예외를 꺼내볼 수 있다.
```java
static void chain_exception() throws HigherLevelException {
    try {
        run();
    } catch (LowerLevelException e) {
        throw new HigherLevelException(e.getMessage(), e);
    }
}
```

예외 발생 시, 로그
```log
// 발생한 예외 (좀 더 자세하게 나온다. 근본 원인까지 출력된다.)
Exception in thread "main" me.iseunghan.item73.HigherLevelException: lower level exception
	at me.iseunghan.item73.BestPracticeException.chain_exception(BestPracticeException.java:37)
	at me.iseunghan.item73.BestPracticeException.main(BestPracticeException.java:16)
Caused by: me.iseunghan.item73.LowerLevelException: lower level exception
	at me.iseunghan.item73.BestPracticeException.run(BestPracticeException.java:29)
	at me.iseunghan.item73.BestPracticeException.chain_exception(BestPracticeException.java:35)
	... 1 more
Caused by: me.iseunghan.item73.LowerLevelException: lower level exception
Execution failed for task ':me.iseunghan.item73.BestPracticeException.main()'.
> Process 'command '/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/java'' finished with non-zero exit value 1
```

## 3. 예외 스누즈 (로깅)
클라이언트에게는 예외를 알리지 말고, 적절한 값으로 반환시킨 다음 logging 라이브러리를 통해 예외 로그를 남겨 추후에 로그를 분석하여 해결하는 방법도 있다. 이렇게 하면 클라이언트에게는 중단없는 API를 제공하고, 로그를 추적할 수 있게끔 마련할 수 있다.
```java
static void snooze_exception() {
    try {
        run();
    } catch (LowerLevelException e) {
        log.error("class: {}, message: {}", e.getClass(), e.getMessage());
    }
}
```