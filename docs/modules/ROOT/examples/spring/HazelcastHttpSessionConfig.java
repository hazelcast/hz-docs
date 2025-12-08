/*
 * Copyright 2014-present the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package docs.http;

import com.hazelcast.config.Config;
import com.hazelcast.config.IndexConfig;
import com.hazelcast.config.IndexType;
import com.hazelcast.core.Hazelcast;
import com.hazelcast.core.HazelcastInstance;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import com.hazelcast.spring.session.HazelcastIndexedSessionRepository;
import com.hazelcast.spring.session.HazelcastSessionConfiguration;
import com.hazelcast.spring.session.config.annotation.web.http.EnableHazelcastHttpSession;

// tag::config[]
@EnableHazelcastHttpSession // <1>
@Configuration
public class HazelcastHttpSessionConfig {


	@Bean
	public HazelcastInstance hazelcastInstance() {
		Config config = new Config();
        HazelcastSessionConfiguration.applySerializationConfig(config); // <2>
		config.getMapConfig(HazelcastIndexedSessionRepository.DEFAULT_SESSION_MAP_NAME) // <3>
			.addIndexConfig(
					new IndexConfig(IndexType.HASH, HazelcastIndexedSessionRepository.PRINCIPAL_NAME_ATTRIBUTE));
		return Hazelcast.newHazelcastInstance(config); // <4>
	}

}
// end::config[]
