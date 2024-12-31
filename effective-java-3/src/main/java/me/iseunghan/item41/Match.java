package me.iseunghan.item41;

public class Match {
    private int headerAttempt;
    private int middleShootAttempt;

    public Match() {
    }

    public Match(int headerAttempt, int middleShootAttempt) {
        this.headerAttempt = headerAttempt;
        this.middleShootAttempt = middleShootAttempt;
    }

    public int getHeaderAttempt() {
        return headerAttempt;
    }

    public void setHeaderAttempt(int headerAttempt) {
        this.headerAttempt = headerAttempt;
    }

    public int getMiddleShootAttempt() {
        return middleShootAttempt;
    }

    public void setMiddleShootAttempt(int middleShootAttempt) {
        this.middleShootAttempt = middleShootAttempt;
    }
}
