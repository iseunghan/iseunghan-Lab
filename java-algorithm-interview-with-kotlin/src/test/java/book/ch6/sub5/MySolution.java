package book.ch6.sub5;

import org.junit.jupiter.api.Test;

import java.util.*;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MySolution {
    @Test
    void test() {
        List<List<String>> answer = groupAnagrams(new String[]{"eat", "tea", "tan", "ate", "nat", "bat"});
        System.out.println(answer);
    }

    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> strings = new HashMap<>(strs.length);

        for (String s : strs) {
            // key를 가져와서 문자열을 하나씩 비교
            // 만약 모든 문자열이 동일하다면, 원소로 추가
            // 아니라면 PASS
            char[] chars = s.toCharArray();
            Arrays.sort(chars);
            String arragedStr = String.valueOf(chars);

            if (!strings.containsKey(arragedStr)) {
                strings.put(arragedStr, new ArrayList<>());
            }
            strings.get(arragedStr).add(s);
        }

        return new ArrayList<>(strings.values());
    }
}
