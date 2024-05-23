package me.iseunghan.configurationproperty.config.v3_use_constructor;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(classes = {TestV3Config.class})
class MyServicePropertyTest {
    @Autowired
    private MyServiceProperty myServiceProperty;

    @Test
    void propertyTest() {
        assertThat(myServiceProperty.isEnabled()).isFalse();
        assertThat(myServiceProperty.getRemoteAddress()).isEqualTo("192.168.1.1");
        assertThat(myServiceProperty.getSecurity().getUsername()).isEqualTo("uname1");
        assertThat(myServiceProperty.getSecurity().getPassword()).isEqualTo("pass1");
        assertThat(myServiceProperty.getSecurity().getRoles()).containsExactlyInAnyOrder("USER", "ADMIN");
    }
}
