package me.iseunghan.item34;

public class OperationTest {
    public static void main(String[] args) {
        double x = 2d;
        double y = 1d;
        for (Operation op : Operation.values()) {
            System.out.printf("%f %s %f = %f%n", x, op, y, op.apply(x, y));
        }

        System.out.println("------------------------------------------");

        for (int i = 0; i < 5; i++) {
            Operation operation = Operation.fromString(i + "A")
                    .orElseThrow();
            System.out.println(operation);
        }
    }

}
