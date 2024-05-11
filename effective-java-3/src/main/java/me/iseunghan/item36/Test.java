package me.iseunghan.item36;

import java.util.EnumSet;

public class Test {
    public static void main(String[] args) {
        Wrong_Text text1 = new Wrong_Text();
        text1.applyStyles(Wrong_Text.STYLE_BOLD | Wrong_Text.STYLE_STRIKETHROUGH);
        text1.applyStyles(Wrong_Text.STYLE_BOLD | Wrong_Text.STYLE_STRIKETHROUGH | 1);  // 이런 불상사가 발생한다!

        BestPractice_Text text2 = new BestPractice_Text();
        text2.apply(EnumSet.of(BestPractice_Text.Style.BOLD, BestPractice_Text.Style.STRIKETHROUGH));
    }
}
