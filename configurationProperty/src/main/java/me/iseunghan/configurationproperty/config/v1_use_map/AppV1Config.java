package me.iseunghan.configurationproperty.config.v1_use_map;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@EnableConfigurationProperties(MyServiceProperty.class)
@Configuration
public class AppV1Config {
}
