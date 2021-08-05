import com.hazelcast.nio.ObjectDataInput;
import com.hazelcast.nio.ObjectDataOutput;
import com.hazelcast.nio.serialization.DataSerializable;

import java.io.IOException;

//tag::address[]
public class Address implements DataSerializable {
    private String street;
    private int zipCode;
    private String city;
    private String state;

    public Address() {}

    //getters setters..

    public void writeData( ObjectDataOutput out ) throws IOException {
        out.writeString(street);
        out.writeInt(zipCode);
        out.writeString(city);
        out.writeString(state);
    }

    public void readData( ObjectDataInput in ) throws IOException {
        street = in.readString();
        zipCode = in.readInt();
        city = in.readString();
        state = in.readString();
    }
}
//end::address[]