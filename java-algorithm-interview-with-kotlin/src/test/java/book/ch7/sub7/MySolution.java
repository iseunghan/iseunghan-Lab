package book.ch7.sub7;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MySolution {
    @Test
    void test() {
        int[] result = twoSum(new int[]{2, 7, 11, 15}, 9);
        Assertions.assertArrayEquals(result, new int[]{0, 1});
    }

    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{0, 1};
    }
}
