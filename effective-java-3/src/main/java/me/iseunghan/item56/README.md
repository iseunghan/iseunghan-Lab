# 공개된 API 요소에는 항상 문서화 주석을 작성하라
API를 작성했다면 게다가 이 API를 오픈소스로 공개할 생각이라면 더더욱 API 문서화를 해야만 한다. 자바독(javadoc)이라는 유틸리티가 귀찮고 어려운 이 문서화를 도와 줄 것이다.

### 무엇을 적어야 할까?
- 메서드가 어떻게 동작하는지 보단 -> 무엇을 하는지를 써야한다.
- 메서드를 호출하기 위한 매개변수 등 전제조건을 적어야 한다. (@param)
- 예외를 던진다면 @throws를 통해 알려줘야 한다. (@throws)
- 스레드를 시작하는 거라면 꼭 알려줘야 한다. 
- 반환타입과 어떤 값을 반환하는지에 대한 설명도 있어야 한다. (@return)

### javadoc 문법
```java
/**
 * {@summary 이 리스트에서 지정한 위치의 원소를 반화한다.}
 *
 * <p>이 메서드는 상수 시간에 수행됨을 보장하지 않는다. 
 * ...
 * {@code index < 0 || index >= this.size()}이면 IndexOutOfBoundsException이 발생한다.
 * 
 * @oaram index 반환할 원소의 인덱스; 0이상이고 리스트 크기보다 작아야 함
 * @return 이 리스트에서 지정한 위치의 원소
 * @throws IndexOutOfBoundsException index가 범위를 벗어나면, 즉, ({@code index < 0 || index >= this.size()})이면 발생한다.
 */
E get(int index);
```
- {@summary}: 요약을 작성할 수 있다.
- {@code}: 내부에 코드블럭을 삽입할 수 있다.
- HTML 태그: 자바독은 최종적으로 HTML로 변환되기 때문에, 내부에 HTML 태그들을 사용할 수 있다.
- @param: 매개변수에 대한 설명
- @return: 반환타입에 대한 설명
- @throws: 예외 발생에 대한 설명

### 자주 누락되는 설명
- 스레드 안정성
- 직렬화 가능성  

이 두 가지를 많이 빠뜨린다. 클래스 혹은 정적 메서드가 스레드 안전하든 그렇지 않든, 스레드 안전 수준을 반드시 API 설명에 포함시켜야 한다. 직렬화가 가능하다면 어떤식으로 되는지도 설명해줘야 한다.

### 유용한 커맨드
```shell
-Xdoclint
```
자바독을 올바르게 작성했는지 확인하는 기능

```shell
-html5
```
자바9,10은 기본적으로 html4로 생성하는데 위 옵션을 사용하면 html5로 생성해준다.

더 자세한 내용은 [javadoc-guide](https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html)를 참조하자.