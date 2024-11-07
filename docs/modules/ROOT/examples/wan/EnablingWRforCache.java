import com.hazelcast.config.Config;
import com.hazelcast.config.WanReplicationConfig;
import com.hazelcast.config.WanReplicationRef;
import com.hazelcast.spi.merge.PassThroughMergePolicy;


public class EnablingWRforCache {

    public static void main(String[] args) throws Exception {
//tag::wrcache[]
        Config config = new Config();

        WanReplicationConfig wrConfig = new WanReplicationConfig();
        wrConfig.setName("my-wan-cluster");

        config.addWanReplicationConfig(wrConfig);

        WanReplicationRef cacheWanRef = new WanReplicationRef();
        cacheWanRef.setName("my-wan-cluster");
        cacheWanRef.setMergePolicyClassName(PassThroughMergePolicy.class.getName());
        cacheWanRef.setRepublishingEnabled(true);
        config.getCacheConfig("my-shared-cache").setWanReplicationRef(cacheWanRef);
//end::wrcache[]
    }
}
