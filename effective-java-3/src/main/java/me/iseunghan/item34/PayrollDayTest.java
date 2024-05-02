package me.iseunghan.item34;

public class PayrollDayTest {
    public static void main(String[] args) {
        for (PayrollDay_with_switch p : PayrollDay_with_switch.values()) {
            System.out.println(p.pay(60, 10));
        }
        System.out.println("----------------------------------------");
        for (PayrollDay_graceful p : PayrollDay_graceful.values()) {
            System.out.println(p.pay(60, 10));
        }
    }
}
