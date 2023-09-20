import com.hazelcast.config.NativeMemoryConfig;
import com.hazelcast.memory.Capacity;
import com.hazelcast.memory.MemoryUnit;

public class SampleHDConfiguration {

    public static void main(String[] args) throws Exception{
        //tag::hdconf[]
        Capacity capacity = new Capacity(512, MemoryUnit.MEGABYTES);
        NativeMemoryConfig nativeMemoryConfig =
                new NativeMemoryConfig()
                        .setAllocatorType(NativeMemoryConfig.MemoryAllocatorType.POOLED)
                        .setCapacity(capacity)
                        .setEnabled(true)
                        .setMinBlockSize(16)
                        .setPageSize(1 << 20);
        //end::hdconf[]
    }
}