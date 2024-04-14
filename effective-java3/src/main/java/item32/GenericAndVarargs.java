package item32;

import java.util.List;

public class GenericAndVarargs {
    public static void main(String[] args) {
        dangerous(List.of("string"));

        /**
         * Console output:
         * Exception in thread "main" java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.String (java.lang.Integer and java.lang.String are in module java.base of loader 'bootstrap')
         * 	at item32.GenericAndVarargs.dangerous(GenericAndVarargs.java:14)
         * 	at item32.GenericAndVarargs.main(GenericAndVarargs.java:7)
         */
    }

//    @SuppressWarnings("unchecked")
    @SafeVarargs
    static void dangerous(List<String>... stringList) {
        List<Integer> intList = List.of(42);
        Object[] objects = stringList;
        objects[0] = intList;               // heap 오염
        String s = stringList[0].get(0);    // ClassCastException 발생!
        // 문제 해결방법? -> varargs 변수는 데이터 옮기는 용도로만 사용하고, 절대 데이터 조작을 하지 않도록 강제!
    }
}
