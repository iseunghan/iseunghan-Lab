package me.iseunghan.configurationproperty.config.v2_use_class;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@EnableConfigurationProperties(MyServiceProperty.class)
@Configuration
public class AppV2Config {
}
