package security;

import com.hazelcast.config.Config;
import com.hazelcast.config.PermissionConfig;
import com.hazelcast.config.PermissionConfig.PermissionType;
import com.hazelcast.config.SecurityConfig;
import com.hazelcast.config.security.LdapAuthenticationConfig;
import com.hazelcast.config.security.RealmConfig;
import com.hazelcast.config.security.SimpleAuthenticationConfig;

public class EnablingSecurity {

    public static void main(String[] args) throws Exception{
//tag::es[]
Config cfg = new Config();
SecurityConfig securityCfg = cfg.getSecurityConfig();
securityCfg.setEnabled( true );
//end::es[]
    }

    public static void authenticationSample() throws Exception{
//tag::authn[]
Config cfg = new Config();
SimpleAuthenticationConfig sac = new SimpleAuthenticationConfig()
        .addUser("test", "V3ryS3cr3tString", "monitor", "hazelcast")
        .addUser("man-center", "HardToGuess", "root");
cfg.getSecurityConfig().setEnabled(true)
        .setClientRealmConfig("simpleRealm",
                new RealmConfig().setSimpleAuthenticationConfig(sac));
//end::authn[]
    }

    public static void identitySample() throws Exception{
//tag::identity[]
Config cfg = new Config();
cfg.getSecurityConfig()
    .setEnabled(true)
    .addRealmConfig("aRealm", 
        new RealmConfig().setLdapAuthenticationConfig(new LdapAuthenticationConfig()/* ... */)
            .setUsernamePasswordIdentityConfig("uid=hazelcast,ou=Services,dc=hazelcast,dc=com", "theSecret"))
    .setClientRealm("aRealm")
    .setMemberRealm("aRealm");
//end::identity[]
    }

    public static void authorizationSample() throws Exception{
//tag::authz[]
Config cfg = new Config();
cfg.getSecurityConfig()
    .setEnabled(true)
    .setClientRealmConfig("aRealm", new RealmConfig()/* ... */)
    .addClientPermissionConfig(new PermissionConfig(PermissionType.ALL, null, "man-center"))
    .addClientPermissionConfig(new PermissionConfig(PermissionType.MAP, "playground", "*").addAction("all"));
//end::authz[]
    }

}
