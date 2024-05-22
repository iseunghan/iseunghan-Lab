package me.iseunghan.configurationproperty.config.v2_use_class;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.ArrayList;
import java.util.List;

@Getter
@Setter
@ConfigurationProperties(prefix = "my.service")
public class MyServiceProperty {
    private boolean enabled;
    private String remoteAddress;
    private Security security;

    @Getter
    @Setter
    public static class Security {
        private String username;
        private String password;
        private final List<String> roles = new ArrayList<>();
    }
}
