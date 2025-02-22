package me.iseunghan.item79;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CopyOnWriteArrayList;

public class ObservableSet_without_synchronized<E> extends ObservableSet<E> {
    public ObservableSet_without_synchronized(Set<E> s) {
        super(s);
    }

    private final List<SetObserver<E>> observers = new CopyOnWriteArrayList<>();

    @Override
    public void addObserver(SetObserver<E> observer) {
        observers.add(observer);
    }

    @Override
    public boolean removeObserver(SetObserver<E> observer) {
        return observers.remove(observer);
    }

    @Override
    protected void notifyElementAdded(E element) {
        for (SetObserver<E> observer : observers) {
            observer.added(this, element);
        }
    }
}
