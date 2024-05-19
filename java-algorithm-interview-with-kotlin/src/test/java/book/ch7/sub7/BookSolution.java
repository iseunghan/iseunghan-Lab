package book.ch7.sub7;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

public class BookSolution {
    @Test
    void test() {
        int[] result1 = bookSolution1(new int[]{2, 7, 11, 15}, 9);
        int[] result2 = bookSolution2(new int[]{2, 7, 11, 15}, 9);
        Assertions.assertArrayEquals(result1, new int[]{0, 1});
        Assertions.assertArrayEquals(result2, new int[]{0, 1});
    }

    /**
     * Map에 값과 인덱스를 키/값으로 넣어두고,
     * nums를 순차적으로 순회하면서 target과의 차이가 Map에 있는지 확인하면 된다!
     * 이렇게하면 시간복잡도는 nums를 순회하는 O(n)이 소요 된다. (Map을 조회하는건 O(1)임)
     */
    public int[] bookSolution1(int[] nums, int target) {
        Map<Integer, Integer> maps = new HashMap<>(nums.length);
        for (int i = 0; i < nums.length; i++) {
            maps.put(nums[i], i);
        }

        for (int i = 0; i < nums.length; i++) {
            if (maps.containsKey(target - nums[i]) && maps.get(target - nums[i]) != i) {
                return new int[]{i, maps.get(target - nums[i])};
            }
        }
        return null;    // not reached
    }

    /**
     * solution1에서 map을 생성하는 코드와 정답을 찾는 코드를 합쳤다.
     * 기존과 동일하게 한번에 target과 현재 인덱스의 값의 차이를 map의 키를 찾고 정답이 있으면 반환하고,
     * 아니라면 맵에 추가하여 정답을 찾는 방식이다.
     * 성능상 큰 이점은 없다.
     */
    public int[] bookSolution2(int[] nums, int target) {
        Map<Integer, Integer> maps = new HashMap<>(nums.length);
        for (int i = 0; i < nums.length; i++) {
            if (maps.containsKey(target - nums[i])) {
                return new int[]{maps.get(target - nums[i]), i};
            }
            maps.put(nums[i], i);
        }
        return null;
    }
}
