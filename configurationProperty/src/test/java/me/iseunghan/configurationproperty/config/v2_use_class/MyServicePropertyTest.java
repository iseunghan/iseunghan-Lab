package me.iseunghan.configurationproperty.config.v2_use_class;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(classes = {AppV2Config.class, MyServiceProperty.class})
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
