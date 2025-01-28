package me.iseunghan.item60;

import java.math.BigDecimal;

public class FinanceCalculator {

    // 부동소수점의 정확성 파악 (근사치를 계산하게끔 설계됨)
    static void test_float_double() {
        System.out.println(1.03 - 0.42);        // 0.6100000000000001
        System.out.println(1.00 - 9 * 0.10);    // 0.09999999999999998
    }

    // 최악의 방법: 정확도가 떨어짐!
    static void test_buy_candy() {
        double funds = 1.00;
        int itemsBought = 0;
        for (double price = 0.10; funds >= price; price += 0.10) {
            funds -= price;
            itemsBought++;
        }
        System.out.println(itemsBought);    // 3
        System.out.println(funds);          // 0.3999999999999999
    }

    // 그나마 나은 방법:
    // 정확도를 높이기 위해 BigDecimal 생성자에 문자열을 사용했다.
    // 하지만, 단점으로는 기본타입보다 쓰기 불편하고, 훨씬 느리다.
    static void test_buy_candy2() {
        final BigDecimal TEN_CENTS = new BigDecimal(".10");

        int itemBought = 0;
        BigDecimal funds = new BigDecimal("1.00");
        for (BigDecimal price = TEN_CENTS; funds.compareTo(price) >= 0; price = price.add(TEN_CENTS)) {
            funds = funds.subtract(price);
            itemBought++;
        }
        System.out.println(itemBought); // 4
        System.out.println(funds);      // 0.00
    }

    // best practice! int, long을 사용하여 센트 단위로 계산을 한다! (소수점이 없다!)
    static void test_buy_candy3() {
        int itemBought = 0;
        int funds = 100;
        for (int price = 10; funds >= price; price += 10) {
            funds -= price;
            itemBought++;
        }
        System.out.println(itemBought); // 4
        System.out.println(funds);      // 0
    }
}
