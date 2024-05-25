package me.iseunghan.configurationproperty.config.v1_use_map;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.ArrayList;
import java.util.LinkedHashMap;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(classes = {AppV1Config.class, MyServiceProperty.class})
class MyServicePropertyTest {

    @Autowired
    private MyServiceProperty myServiceProperty;

    @Test
    void propertyTest() {
        assertThat(myServiceProperty.isEnabled()).isFalse();
        assertThat(myServiceProperty.getRemoteAddress()).isEqualTo("192.168.1.1");
        assertThat(myServiceProperty.getSecurity().get("username")).isEqualTo("uname1");
        assertThat(myServiceProperty.getSecurity().get("password")).isEqualTo("pass1");
        assertThat(((LinkedHashMap<String, String>) myServiceProperty.getSecurity().get("roles")).values()).containsExactlyInAnyOrder("USER", "ADMIN");
    }
}
