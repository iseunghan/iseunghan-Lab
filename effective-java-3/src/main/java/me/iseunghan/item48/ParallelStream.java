package me.iseunghan.item48;

import java.math.BigInteger;
import java.util.stream.LongStream;

public class ParallelStream {
    static long pi_parallel(long n) {
        return LongStream.rangeClosed(2, n)
                .parallel()
                .mapToObj(BigInteger::valueOf)
                .filter(i -> i.isProbablePrime(10))
                .count();
    }

    static long pi(long n) {
        return LongStream.rangeClosed(2, n)
                .mapToObj(BigInteger::valueOf)
                .filter(i -> i.isProbablePrime(10))
                .count();
    }

    public static void main(String[] args) {
        long start = System.currentTimeMillis();
        pi(999999);
        System.out.println(System.currentTimeMillis() - start); // about 656ms

        start = System.currentTimeMillis();
        pi_parallel(999999);
        System.out.println(System.currentTimeMillis() - start); // about 113ms
    }
}
