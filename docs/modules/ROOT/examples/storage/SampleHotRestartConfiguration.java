import com.hazelcast.config.*;

import java.io.File;

public class SamplePersistenceConfiguration {

    public static void main(String[] args) throws Exception{
        //tag::hrconf[]
        Config config = new Config();
        PersistenceConfig PersistenceConfig = new PersistenceConfig()
        .setEnabled(true)
        .setBaseDir(new File("/mnt/persistence"))
        .setParallelism(1)
        .setValidationTimeoutSeconds(120)
        .setDataLoadTimeoutSeconds(900)
        .setClusterDataRecoveryPolicy(PersistenceClusterDataRecoveryPolicy.FULL_RECOVERY_ONLY)
        .setAutoRemoveStaleData(true);
        config.setPersistenceConfig(PersistenceConfig);

        MapConfig mapConfig = config.getMapConfig("test-map");
        mapConfig.getDataPersistenceConfig().setEnabled(true);

        CacheSimpleConfig cacheConfig = config.getCacheConfig("test-cache");
        cacheConfig.getDataPersistenceConfig().setEnabled(true);
        //end::hrconf[]
    }
}