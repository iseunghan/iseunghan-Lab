package me.iseunghan;

import java.util.List;

public class LambdaExample1 {
    // basic codes
    public int getTotalHeadersAttempt(List<Match> matches) {
        int sumOfHeaderAttempt = 0;
        for (Match match : matches) {
            sumOfHeaderAttempt += match.getHeaderAttempt();
        }
        return sumOfHeaderAttempt;
    }

    public int getTotalMiddleShootAttempt(List<Match> matches) {
        int sumOfMiddleShootAttempt = 0;
        for (Match match : matches) {
            sumOfMiddleShootAttempt += match.getMiddleShootAttempt();
        }
        return sumOfMiddleShootAttempt;
    }

    // refactor codes
    private int calculateTotalCount(List<Match> matches, Counter counter) {
        int count = 0;
        for (Match match : matches) {
            count += counter.getCountOfStat(match);
        }
        return count;
    }

    public int getTotalHeadersAttemptRefactor(List<Match> matches) {
        return calculateTotalCount(matches, Match::getHeaderAttempt);
    }

    public int getTotalMiddleShootAttemptRefactor(List<Match> matches) {
        return calculateTotalCount(matches, Match::getMiddleShootAttempt);
    }
}
