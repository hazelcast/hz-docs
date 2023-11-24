import com.hazelcast.core.Hazelcast;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.cp.CPMap;

public class ExampleCPMap {

    public static void main( String[] args ) {
        //tag::cpm[]
        HazelcastInstance hazelcastInstance = Hazelcast.newHazelcastInstance();
        // creates 'capitalCities' CPMap in the 'default' CP Group
        CPMap<String, String> capitalCities = hazelcastInstance.getCPSubsystem().getMap("capitalCities");
        // prefer 'set' over 'put' when the previous value associated with a key is not required
        capitalCities.set("England", "London");
        assert "London".equals(capitalCities.get("England"));
        assert null == capitalCities.put("France", "Paris");
        assert "London".equals(capitalCities.remove("England"));
        // prefer 'delete' over 'remove' when the value associated with the key is not required
        capitalCities.delete("France");
        capitalCities.set("Germany", "Munich");
        assert capitalCities.compareAndSet("Germany", "Munich", "Berlin");
        assert "Berlin".equals(capitalCities.get("Germany"));
        capitalCities.destroy();
        //end::cpm[]
    }
}
