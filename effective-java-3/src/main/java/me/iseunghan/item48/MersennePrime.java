package me.iseunghan.item48;

import java.math.BigInteger;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.TWO;

// 메르센 소수
public class MersennePrime {
    public static void main(String[] args) {
        primes().map(p -> TWO.pow(p.intValueExact()).subtract(ONE)) // intValueExact 함수는 BigInteger -> Integer 변환에 실패할 때, 예외를 발생시킨다. intValue()는 오버플로가 나도 그냥 반환한다.
                .filter(mersenne -> mersenne.isProbablePrime(50))   // 50 (certainty)은 소수를 판별하기 위한 척도이다. 50까지의 수 가지고 판별하겠다는 의미이다. 웬만한 숫자들은 10까지 커버가 가능한것으로 안다.
                .limit(20)
                .forEach(System.out::println);

        // intValue(), intValueExact()의 차이를 실습.
//        System.out.println(BigInteger.valueOf(1231250123081290112L).pow(1213214).intValue());       //        0
//        System.out.println(BigInteger.valueOf(1231250123081290112L).pow(1213214).intValueExact());  //        Exception in thread "main" java.lang.ArithmeticException: BigInteger out of int range
                                                                                                            //        at java.base/java.math.BigInteger.intValueExact(BigInteger.java:4858)
                                                                                                            //        at me.iseunghan.item48.MersennePrime.main(MersennePrime.java:18)
    }

    static Stream<BigInteger> primes() {
        return Stream.iterate(TWO, BigInteger::nextProbablePrime);
    }
}
