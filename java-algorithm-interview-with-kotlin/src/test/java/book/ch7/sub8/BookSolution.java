package book.ch7.sub8;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class BookSolution {
    @Test
    void test() {
        int result = trap1(new int[]{0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1});
        Assertions.assertEquals(result, 6);
    }

    /**
     * 투 포인터로 해결하는 풀이 (풀이가 너무 대단하다)
     * - 가장 높은 쪽을 향해서 투 포인터를 움직이는 것
     * - MaxHeight를 이용해서 차이를 구해 result에 추가하는 것
     */
    public int trap1(int[] height) {
        int result = 0;
        int left = 0;
        int right = height.length - 1;
        int leftMax = height[left];
        int rightMax = height[right];

        while (left < right) {
            leftMax = Math.max(leftMax, height[left]);
            rightMax = Math.max(rightMax, height[right]);

            if (leftMax <= rightMax) {
                result += leftMax - height[left];
                left++;
            } else {
                result += rightMax - height[right];
                right--;
            }
        }
        return result;
    }
}
