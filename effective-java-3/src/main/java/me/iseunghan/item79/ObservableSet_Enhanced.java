package me.iseunghan.item79;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Set;

public class ObservableSet_Enhanced<E> extends ObservableSet<E> {
    public ObservableSet_Enhanced(Set<E> s) {
        super(s);
    }

    private final List<SetObserver<E>> observers = new ArrayList<>();

    @Override
    public void addObserver(SetObserver<E> observer) {
        synchronized (observers) {
            observers.add(observer);
        }
    }

    @Override
    public boolean removeObserver(SetObserver<E> observer) {
        synchronized (observers) {
            return observers.remove(observer);
        }
    }

    @Override
    protected void notifyElementAdded(E element) {
        List<SetObserver<E>> copyList;

        synchronized (observers) {
            copyList = new ArrayList<>(observers);
        }

        for (SetObserver<E> observer : copyList) {
            observer.added(this, element);
        }
    }
}
