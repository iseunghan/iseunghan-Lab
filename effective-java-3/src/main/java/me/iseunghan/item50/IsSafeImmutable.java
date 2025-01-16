package me.iseunghan.item50;

import java.util.Date;

public class IsSafeImmutable {
    public static void main(String[] args) {
        isFirstPeriod_Immutable();
        isSecondPeriod_Immutable();
        isThirdPeriod_Immutable();
    }

    /**
     * Period는 완벽한 불변객체라 생각했지만, 실은 Date가 가변객체임을 알지 못하여서 불변객체가 아니게 된다.
     */
    static void isFirstPeriod_Immutable() {
        Date start = new Date();
        Date end = new Date();
        FirstPeriod p = new FirstPeriod(start, end);
        end.setYear(2024);  // p의 내부를 수정하였다. 이래도 Period는 불변인가?
        System.out.println(p.getEnd() == end);  // true
    }

    public final static class FirstPeriod {
        private final Date start;
        private final Date end;

        public FirstPeriod(Date start, Date end) {
            if (start.after(end)) throw new IllegalArgumentException("start faster than end!");
            this.start = start;
            this.end = end;
        }

        public Date getStart() {
            return start;
        }

        public Date getEnd() {
            return end;
        }
    }

    /**
     * 생성자의 방어적 복사로 내부가 수정되는 일을 막았다. 근데 이게 정말 다일까?
     */
    static void isSecondPeriod_Immutable() {
        Date start = new Date();
        Date end = new Date();
        SecondPeriod p = new SecondPeriod(start, end);
        end.setYear(2024);  // p의 내부를 수정하였다. 이래도 Period는 불변인가?
        System.out.println(p.getEnd() == end);  // false
    }

    public final static class SecondPeriod {
        private final Date start;
        private final Date end;

        public SecondPeriod(Date start, Date end) {
            if (start.after(end)) throw new IllegalArgumentException("start faster than end!");
            this.start = new Date(start.getTime());
            this.end = new Date(end.getTime());
//            this.end = (Date) end.clone();  // clone() 메서드를 쓰지 않는 이유? clone()을 Date가 구현한게 아닐지도 모른다.
        }

        public Date getStart() {
            return start;
        }

        public Date getEnd() {
            return end;
        }
    }

    /**
     * Period는 완벽한 불변객체라 생각했지만, 실은 Date가 가변객체임을 알지 못하여서 불변객체가 아니게 된다.
     */
    static void isThirdPeriod_Immutable() {
        Date start = new Date();
        Date end = new Date();
        SecondPeriod p = new SecondPeriod(start, end);
        p.getEnd().setYear(2024);
        System.out.println(p.getEnd().getYear() == 2024);  // true

        //--------------------------------------------------
        // 이제 get 접근자까지 방어적 복사를 해야한다.
        Date start2 = new Date();
        Date end2 = new Date();
        ThirdPeriod p2 = new ThirdPeriod(start2, end2);
        p2.getEnd().setYear(2024);
        System.out.println(p2.getEnd().getYear() == 2024);  // false
    }

    // 이제 비로소 완벽한 불변객체가 되었다!
    public final static class ThirdPeriod {
        private final Date start;
        private final Date end;

        public ThirdPeriod(Date start, Date end) {
            if (start.after(end)) throw new IllegalArgumentException("start faster than end!");
            this.start = new Date(start.getTime());
            this.end = new Date(end.getTime());
        }

        public Date getStart() {
            return new Date(start.getTime());
        }

        public Date getEnd() {
            return new Date(end.getTime());
        }
    }
}
