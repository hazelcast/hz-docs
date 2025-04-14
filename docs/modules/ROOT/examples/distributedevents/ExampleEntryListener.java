import com.hazelcast.core.EntryEvent;
import com.hazelcast.core.EntryListener;
import com.hazelcast.map.MapEvent;

//tag::mm[]
public class ExampleEntryListener implements EntryListener<String, String> {
    @Override
    public void entryAdded(EntryEvent<String, String> event) {
        System.out.println("Entry Added: " + event);
    }
    @Override
    public void entryRemoved(EntryEvent<String, String> event) {
        System.out.println( "Entry Removed: " + event );
    }
    @Override
    public void mapCleared(MapEvent event) {
        System.out.println( "Map Cleared: " + event );
    }
    @Override
    public void entryUpdated(EntryEvent<String, String> event) {
        // not supported for MultiMap
    }
    @Override
    public void entryEvicted(EntryEvent<String, String> event) {
    }
    @Override
    public void entryExpired(EntryEvent<String, String> event) {
    }
    @Override
    public void mapEvicted(MapEvent event) {
    }
}
//end::mm[]
