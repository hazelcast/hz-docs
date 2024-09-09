import com.hazelcast.config.*;

import java.io.File;

public class SamplePersistenceConfiguration {

    public static void main(String[] args) throws Exception{
        //tag::hrconf[]
        Config config = new Config();
        PersistenceConfig persistenceConfig = new PersistenceConfig()
        .setEnabled(true)
        .setBaseDir(new File("/mnt/persistence"))
        .setParallelism(1)
        .setValidationTimeoutSeconds(120)
        .setDataLoadTimeoutSeconds(900)
        .setClusterDataRecoveryPolicy(PersistenceClusterDataRecoveryPolicy.FULL_RECOVERY_ONLY)
        .setAutoRemoveStaleData(true)
        .setRebalanceDelaySeconds(0);
        config.setPersistenceConfig(persistenceConfig);

        MapConfig mapConfig = config.getMapConfig("test-map");
        mapConfig.getDataPersistenceConfig().setEnabled(true);
        mapConfig.getMerkleTreeConfig().setEnabled(true);
        mapConfig.getMerkleTreeConfig().setDepth(12);
        config.addMapConfig(mapConfig);

        CacheSimpleConfig cacheConfig = config.getCacheConfig("test-cache");
        cacheConfig.getDataPersistenceConfig().setEnabled(true);
        cacheConfig.getMerkleTreeConfig().setEnabled(true);
        cacheConfig.getMerkleTreeConfig().setDepth(12);
        config.addCacheConfig(cacheConfig);

        config.getSqlConfig().setCatalogPersistenceEnabled(true);

        config.getJetConfig().setLosslessRestartEnabled(true);
        //end::hrconf[]
    }
}
