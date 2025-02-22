package me.iseunghan.item62;

public final class ThreadLocal3<T> {
    private ThreadLocal3() {}

    public void set(T value) {
        // do-something
    }

    /**
     * @see java.lang.ThreadLocal
     *
     * <p>
     *
     * 아래는 ThreadLocal.get() 메서드이다. 내부적으로 현재 Thread의 Map을 가져와서 Value를 가져오는 방식이다.
     * public T get() {
     *         Thread t = Thread.currentThread();
     *         ThreadLocalMap map = getMap(t);
     *         if (map != null) {
     *             ThreadLocalMap.Entry e = map.getEntry(this);
     *             if (e != null) {
     *                 @SuppressWarnings("unchecked")
     *                 T result = (T)e.value;
     *                 return result;
     *             }
     *         }
     *         return setInitialValue();
     *     }
     */
    public T get() {
        // do-something
        return null;    // 여기서도 내부적으로 ValueMap에서 꺼내오게 구현하면 될듯하다.
    }
}
