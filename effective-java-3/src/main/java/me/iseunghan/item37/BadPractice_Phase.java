package me.iseunghan.item37;

public enum BadPractice_Phase {
    // 만약 SOLID 앞에 원소를 추가하면 from()는 기능을 상실해버린다. (뒤부터 채우면 되지 않냐고? 말도 안되는 소리.. 우린 이런걸 안티패턴이라고 부르기로 했어요..)
    SOLID, LIQUID, GAS;

    public enum Transition {
        MELT, FREEZE, BOIL, CONDENSE, SUBLIME, DEPOSIT;

        private static final Transition[][] TRANSITIONS = {
                {null, MELT, SUBLIME},
                {FREEZE, null, BOIL},
                {DEPOSIT, CONDENSE, null}
        };

        public static Transition from(BadPractice_Phase from, BadPractice_Phase to) {
            return TRANSITIONS[from.ordinal()][to.ordinal()];   // *ordinal을 사용하면 Phase의 값이 추가되면 어떻게 대응할 것인지?
        }
    }
}
