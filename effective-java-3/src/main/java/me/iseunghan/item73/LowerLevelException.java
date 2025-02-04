package me.iseunghan.item73;

public class LowerLevelException extends HigherLevelException {
    public LowerLevelException(String message, Throwable cause) {
        super(message, cause);
    }

    public LowerLevelException(String message) {
        super(message);
    }

    public LowerLevelException() {
        super("lower level exception");
    }
}
