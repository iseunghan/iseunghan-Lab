### 비트 필드 대신 EnumSet을 사용하라
```java
public class Wrong_Text {
    public static final int STYLE_BOLD = 1 << 0;
    public static final int STYPE_ITALIC = 1 << 1;
    public static final int STYLE_UNDERLINE = 1 << 2;
    public static final int STYLE_STRIKETHROUGH = 1 << 3;

    public void applyStyles(int styles) {
        // do something..
    }
}
```
여러 스타일을 적용시켜야 해서 비트 필드를 static final로 선언해서 사용하고 있다.
하지만 int 타입이므로 다음과 같은 상황들을 막지 못한다.
```java
Wrong_Text text1 = new Wrong_Text();
text1.applyStyles(Wrong_Text.STYLE_BOLD | Wrong_Text.STYLE_STRIKETHROUGH);
text1.applyStyles(Wrong_Text.STYLE_BOLD | Wrong_Text.STYLE_STRIKETHROUGH | 1);  // 이런 불상사가 발생한다!
```
게다가 비트값이기 때문에 해석하기도 어렵다. 그리고 비트 피드 하나에 녹아있는 모든 원소를 순회하기도 까다롭다

위 애로사항들을 EnumSet을 이용해 해결할 수 있다.
  
#### EnumSet을 사용하라
```java
import java.util.Set;

public class BestPractice_Text {
    public enum Style { BOLD, ITALIC, UNDERLINE, STRIKETHROUGH }

    public void apply(Set<Style> styles) {
        // do something..
    }
}
```
클래스 내부 Enum으로 선언하게 되면, 타입 안정성을 최대한 끌어올릴 수 있다.
apply 함수는 EnumSet이 아닌 Set 타입으로 받는 이유는 인터페이스 타입으로 선언하는게 좋은 습관이다(아이템 64) + OCP 원칙 적용.   
나중에 이상한 클라이언트가 EnumSet이 아닌 Set을 추가한다고 했을 때 완벽하게 커버된다.  
사용도 다음과 같이 하면 된다.  
```java
BestPractice_Text text2 = new BestPractice_Text();
text2.apply(EnumSet.of(BestPractice_Text.Style.BOLD, BestPractice_Text.Style.STRIKETHROUGH));
```
apply 함수가 Set 타입을 받고 있기 때문에 타입 안정성 측면에서 좋다.  
게다가 EnumSet 내부는 비트 벡터로 구현되어 있기 때문에 성능도 뒤쳐지지 않는다(64개 이하일 경우).