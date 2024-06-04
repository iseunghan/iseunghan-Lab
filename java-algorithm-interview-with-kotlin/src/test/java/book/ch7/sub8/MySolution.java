package book.ch7.sub8;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class MySolution {
    @Test
    void test() {
        int result = trap(new int[]{0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1});
        Assertions.assertEquals(result, 6);
    }

    /**
     * 투 포인터로 해결해보려했지만, 잘못 사용하여 실패하였다.
     */
    public int trap(int[] height) {
        int result = 0;
        int max_index = height.length - 1;
        int p1 = 1;
        int p2 = 1;
        int tp1 = 0;
        int tp2 = 0;
        int max_height = 0;

        while (p1 > 0 && p2 < max_index) {
            tp1 = p1;
            tp2 = p2;

            while (tp1 > 0 && height[tp1 - 1] >= height[tp1]) {tp1--;}
            while (tp2 < max_index && height[tp2 + 1] >= height[tp2]) {tp2++;}

            if (
                    height[tp1] > height[tp1 + 1] &&
                            height[tp2] > height[tp2 - 1]
            ) {
                max_height = Math.max(height[tp1], height[tp2]);
                System.out.println(">> :" + tp1 + ", " + tp2);
                for (int i=tp1 + 1; i<tp2; i++) {
                    System.out.println("add :" + (max_height - height[i]));
                    result += max_height - height[i];
                }
            }
            p1 = tp2 + 1;
            p2 = p1;
        }

        return result;
    }
}
