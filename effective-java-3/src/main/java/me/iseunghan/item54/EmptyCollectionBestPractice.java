package me.iseunghan.item54;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class EmptyCollectionBestPractice {
    private final List<String> cheesesInStock = new ArrayList<>();

    /**
     * null을 반환하게 되면, client에서는 또 null 처리를 해줘야 하는 불편함이 생긴다.
     */
    public List<String> getCheeses_bad() {
        return cheesesInStock.isEmpty() ? null : new ArrayList<>(cheesesInStock);
    }

    /**
     * 매번 비어있는 리스트를 반환하면 성능이 저하되는거 아니냐고? 아니다. null을 리턴하는 것과 별반 차이가 없다.
     * 게다가 emptyList는 내부에 정적 변수로 선언되어있으므로 안심된다.
     */
    public List<String> getCheeses_best() {
        return cheesesInStock.isEmpty() ? Collections.emptyList() : new ArrayList<>(cheesesInStock);
    }

    public String[] getCheeses_arr_bad() {
        return cheesesInStock.toArray(new String[cheesesInStock.size()]);
    }

    /**
     * 아예 비어있는 배열을 정적변수로 만들어놓고 써라. toArray는 cheeseInStock이 비어있으면 EMPTY_CHEESE_ARRAY를 반환할것이고, 아니라면 해당 arr를 가지고 새롭게 생성해서 반환할 것이다.
     * 성능 개선 목적이라면, toArray에 넘기는 배열의 0이 아닌 사이즈로 초기화 시키지마라. 성능이 떨어진다는 결과가 있다.
     */
    private static final String[] EMPTY_CHEESE_ARRAY = new String[0];
    public String[] getCheeses_arr_best() {
        return cheesesInStock.toArray(EMPTY_CHEESE_ARRAY);
    }
}
