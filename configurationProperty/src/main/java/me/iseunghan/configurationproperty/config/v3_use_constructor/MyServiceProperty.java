package me.iseunghan.configurationproperty.config.v3_use_constructor;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.List;

@Getter
@RequiredArgsConstructor
@ConfigurationProperties(prefix = "my.service")
public class MyServiceProperty {
    private final boolean enabled;
    private final String remoteAddress;
    private final Security security;

    @Getter
    @RequiredArgsConstructor
    public static class Security {
        private final String username;
        private final String password;
        private final List<String> roles;
    }
}
