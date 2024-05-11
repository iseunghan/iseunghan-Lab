package me.iseunghan.item35;

public class Test {
    public static void main(String[] args) {
        // 만약 Wrong_Ensemble에 중간의 값을 추가한다면..?
        // Wrong_Ensemble.numberOfMusicians를 쓰는 곳을 전부 찾아서 다 고쳐야 한다.
        int numberOfMusicians = Wrong_Ensemble.DECTET.numberOfMusicians();

        // 이제 순서에 상관없이 막 추가하고 지워도 된다!
        int numberOfMusicians1 = BestPractice_Ensemble.DECTET.getNumberOfMusicians();
    }
}
