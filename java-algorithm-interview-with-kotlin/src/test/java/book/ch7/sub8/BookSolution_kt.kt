package book.ch7.sub8

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BookSolution_kt {

    @Test
    fun test() {
        val heights = intArrayOf(0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1)
        Assertions.assertEquals(trap(heights), 6);
    }

    fun trap(height: IntArray): Int {
        var volume = 0
        var left = 0
        var right = height.size - 1
        var leftMax = height[left]
        var rightMax = height[right]

        while (left < right) {
            if (height[left] <= height[right]) {
                leftMax = leftMax.coerceAtLeast(height[left])
                volume += leftMax - height[left]
                left++;
            } else {
                rightMax = rightMax.coerceAtLeast(height[right])
                volume += rightMax - height[right]
                right--;
            }
        }
        return volume
    }
}