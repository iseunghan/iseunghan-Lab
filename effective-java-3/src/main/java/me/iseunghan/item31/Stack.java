package me.iseunghan.item31;

import java.util.Arrays;
import java.util.Collection;

public class Stack<E> {
    private E[] e;
    private int index;

    @SuppressWarnings("warnings")
    public Stack() {
        this.e = (E[]) new Object[100];
    }

    public void push(E e) {
        System.out.println("원소를 추가합니다. [" + index + "]: " + e);
        this.e[index++] = e;
    }

    public void pushAll(Iterable<? extends E> src) {
        for (E e1 : src) {
            push(e1);
        }
    }

    public boolean isEmpty() {
        return this.index == 0;
    }

    public E pop() {
        E e1 = this.e[minusAndGetIndex()];
        System.out.println("원소를 삭제합니다. [" + index + "]: " + e1);
        this.e[index] = null;
        return e1;
    }

    private int minusAndGetIndex() {
        return index > 0 ? --index : index;
    }

    public void popAll(Collection<? super E> dst) {
        while (!isEmpty()) {
            dst.add(pop());
        }
    }

    @Override
    public String toString() {
        return "Stack{" +
                "e=" + Arrays.toString(e) +
                ", index=" + index +
                '}';
    }
}
