package storage;

import com.hazelcast.config.EncryptionAtRestConfig;
import com.hazelcast.config.PersistenceConfig;
import com.hazelcast.config.JavaKeyStoreSecureStoreConfig;
import com.hazelcast.config.SSLConfig;
import com.hazelcast.config.SecureStoreConfig;
import com.hazelcast.config.VaultSecureStoreConfig;

import java.io.File;

public class SampleEncryptionAtRestConfiguration {

    public static void main(String[] args) throws Exception{
        //tag::encryptionatrest[]
        PersistenceConfig PersistenceConfig = new PersistenceConfig();
        EncryptionAtRestConfig encryptionAtRestConfig =
                PersistenceConfig.getEncryptionAtRestConfig();
        encryptionAtRestConfig.setEnabled(true)
                .setAlgorithm("AES/CBC/PKCS5Padding")
                .setSecureStoreConfig(/* pass in a configuration object for a secure store here */);
        //end::encryptionatrest[]
        //tag::keystore[]
        JavaKeyStoreSecureStoreConfig keyStoreConfig =
                new JavaKeyStoreSecureStoreConfig(new File("/path/to/keystore.file"))
                        .setType("PKCS12")
                        .setPassword("password")
                        .setCurrentKeyAlias("current")
                        .setPollingInterval(60);
        //end::keystore[]
        //tag::vault[]
        VaultSecureStoreConfig vaultConfig =
                new VaultSecureStoreConfig("http://localhost:1234", "secret/path", "token")
                        .setPollingInterval(60);
        configureSSL(vaultConfig.getSSLConfig());
        //end::vault[]
    }

    private static void configureSSL(SSLConfig sslConfig) {
    }
}