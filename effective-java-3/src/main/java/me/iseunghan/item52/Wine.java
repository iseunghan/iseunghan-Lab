package me.iseunghan.item52;

public class Wine {
    String name() {
        return "포도주";
    }
}

class SparklingWine extends Wine {
    @Override
    String name() {
        return "발포성 포도주";
    }
}

class Champagne extends Wine {
    @Override
    String name() {
        return "샴페인";
    }
}
