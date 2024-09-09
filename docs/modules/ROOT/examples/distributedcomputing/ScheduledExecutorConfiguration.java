import com.hazelcast.config.Config;
import com.hazelcast.config.MergePolicyConfig;
import com.hazelcast.core.Hazelcast;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.scheduledexecutor.IScheduledExecutorService;
import com.hazelcast.config.ScheduledExecutorConfig;

public class ScheduledExecutorConfiguration {
    public static void main(String[] args) throws Exception{
        //tag::sec[]
        Config config = new Config();
        config.getScheduledExecutorConfig( "myScheduledExecSvc" )
              .setPoolSize ( 16 )
              .setCapacityPolicy( ScheduledExecutorConfig.CapacityPolicy.PER_PARTITION )
              .setCapacity( 100 )
              .setDurability( 1 )
              .setMergePolicyConfig( new MergePolicyConfig("com.hazelcast.spi.merge.PassThroughMergePolicy", 110) )
              .setSplitBrainProtectionName( "splitbrainprotectionname" );

        HazelcastInstance hazelcast = Hazelcast.newHazelcastInstance(config);
        IScheduledExecutorService myScheduledExecSvc = hazelcast.getScheduledExecutorService("myScheduledExecSvc");
        //end::sec[]
    }
}
