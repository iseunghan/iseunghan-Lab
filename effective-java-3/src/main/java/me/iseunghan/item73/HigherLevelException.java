package me.iseunghan.item73;

public class HigherLevelException extends Exception {
    public HigherLevelException(String message, Throwable cause) {
        super(message, cause);
    }

    public HigherLevelException(String message) {
        super(message);
    }

    public HigherLevelException() {
        super("higher level exception");
    }
}
