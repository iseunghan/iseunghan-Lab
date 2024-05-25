package me.iseunghan.configurationproperty.config.v1_use_map;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Getter
@Setter
@ConfigurationProperties(prefix = "my.service")
public class MyServiceProperty {
    private boolean enabled;
    private String remoteAddress;
    private final Map<String, Object> security = new HashMap<>();
}
