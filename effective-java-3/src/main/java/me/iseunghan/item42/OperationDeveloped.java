package me.iseunghan.item42;

import java.util.Optional;
import java.util.function.DoubleBinaryOperator;

/**
 * this enum class is develop from below code.
 * {@link me.iseunghan.item34.Operation}
 * new functionalInterface: `DoubleBinaryOperator`
 */
public enum OperationDeveloped {
    PLUS("+", (x, y) -> x + y),
    MINUS("-", (x, y) -> x - y),
    TIMES("-", (x, y) -> x * y),
    DIVIDE("/", (x, y) -> x / y),
    ;

    private final String symbol;
    private final DoubleBinaryOperator operator;

    OperationDeveloped(String symbol, DoubleBinaryOperator operator) {
        this.symbol = symbol;
        this.operator = operator;
    }

    @Override
    public String toString() {
        return this.symbol;
    }

    public double apply(double x, double y) {
        return this.operator.applyAsDouble(x, y);
    }
}
