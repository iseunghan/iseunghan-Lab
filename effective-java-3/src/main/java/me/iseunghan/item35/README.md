### ordinal() 메서드말고 인스턴스 필드를 사용하자
```java
public enum Wrong_Ensemble {
    SOLO, DUET, TRIO, QUARTET, QUINTET, SEXTET, SEPTET, OCTET, NONET, DECTET;

    public int numberOfMusicians() {
        return ordinal() + 1;
    }
}
```
각 단어의 의미가 1중주, 2중주 .. 10중주를 의미한다. 각 중주의 연주자는 몇 명 있는지도 함께 알면 좋을 것 같아서 인스턴스 필드 대신 Enum의 ordinal()이라는 메서드가 순서를 출력하니 단어들을 순서대로 정의하였고 `난 역시 최고야 불필요한 메서드를 만들지 않았어!` 라며 행복회로를 돌렸다.

하지만 문제가 발생했다.  
알고보니 복4중주라는게 있어 8중주 자리 옆에 새로 추가해야 하는 것이 아닌가..!?  
젠장.. 8중주 이후로 순서가 다 밀린다.  

유지보수하려했더니 해당 메서드를 여기저기서 쓰고있었고 일일히 다 고쳐야 했다. 최악...  

#### 필요한 정보가 있다면 인스턴스 필드를 사용하라
```java
public enum BestPractice_Ensemble {
    SOLO(1), DUET(2), TRIO(3), QUARTET(4), QUINTET(5), SEXTET(6), SEPTET(7), OCTET(8), NONET(9), DECTET(10);

    private final int numberOfMusicians;

    BestPractice_Ensemble(int numberOfMusicians) {
        this.numberOfMusicians = numberOfMusicians;
    }

    public int getNumberOfMusicians() {
        return numberOfMusicians;
    }
}
```
인스턴스 필드로 numberOfMusicians를 선언하고 값을 Enum과 함께 선언해버렸다.
이렇게하면 중간에 추가를 하던 삭제를 하던 아무 상관없다! 이전 코드와는 유지보수가 완전 비교도 안될 정도로 짱 쉽다! 