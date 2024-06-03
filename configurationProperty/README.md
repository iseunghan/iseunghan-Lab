원문: https://iseunghan.tistory.com/483
---

## 개요

application.yml에 설정한 property값들을 @Value로 가져오기보다는 해당 설정을 다루는 객체를 하나 만들어두고 가져다 쓸 수 없을까? 하는 의문에서 출발하였습니다. 찾아보니 스프링 부트에서는 @ConfigurationProperties를 통해 Property를 객체에 저장할 수 있는 방법을 제공하고 있습니다.  [@Value 주입 방식](https://www.notion.so/4b03d0a98ae04b59aff25c6876e6432c?pvs=21)보다 훨씬 더 안전하고 강력한 기능을 제공합니다.

## 1. Dependency 추가

ConfigurationProperties를 사용하기 위해서는 아래 의존성을 추가해주셔야 합니다.

```java
annotationProcessor 'org.springframework.boot:spring-boot-configuration-processor'
```

## 2. application.yml

이번 시간의 예제로 쓰일 application.yml 설정입니다.

```java
my:
	service:
		enabled: false
		remote-address: 192.168.1.1
		security:
			username: "uname1"
			password: "pass1"
			roles:
			- "USER"
			- "ADMIN"
```

## 3. Property 주입 받을 클래스 생성

### 3.1. Setter를 통한 주입

주입 받기 위한 클래스는 다음과 같이 선언할 수 있습니다.

```java
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

```

- `@ConfigurationProperties(”my.service”)`
    - `my.service`가 prefix로 설정되어 그 하위 레벨에 선언된 key/value가 매칭되어 주입됩니다.
    - public 접근지시자로 선언된 Setter가 꼭 필요합니다.
        - 빈 후처리기에서 Setter를 이용해 주입하기 때문

### 3.2. 생성자를 통한 주입

```java
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
```

모든 멤버 변수들을 final로 선언하고 @RequiredArgsConstructor와 @ConstructorBinding을 통해 모든 필드를 매개변수로 하는 생성자를 생성하고 해당 생성자를 통해 프로퍼티를 주입받도록 설정할 수 있습니다.

### 3.3. 프로퍼티 바인딩에 대해서

이번 예제에서 사용했던 yml에서 remote-address는 어떻게 String remoteAddress 필드에 바인딩이 잘되었을까요? ~~(저희가 따로 설정해준건 없는데 말이죠.)~~

| Property | Desc |
| --- | --- |
| my.service.remote-address | 권장되는 Kebab-case 형식 |
| my.service.remoteAddress | Camel-case 형식 |
| my.service.remote_address | Snake-case 형식 |

yml의 키의 포맷은 사람마다 다를 수 있기 때문에 스프링 부트는 이러한 프로퍼티의 키 여러 형식을 자동으로 바인딩할 수 있도록 편리한 Relaxed Binding을 제공(위 3가지에 대해서 매핑 시킵니다)합니다.

## 4. Configuration 클래스에 등록

ConfigurationProperties를 받을 클래스만 만들었다고 끝이 아닙니다. 해당 클래스에 주입을 시켜줄 수 있게 @Configuration이 붙은 클래스에 꼭 해당 클래스를 등록시켜줘야 정상작동합니다. 등록할 수 있는 방법은 총 2가지가 있습니다.

### 4.1. @EnableConfigurationProperties

```java
@EnableConfigurationProperties(MyExampleProperty.class)
@Configuration
public class MyConfig {}
```

@Configuration이 붙은 클래스에 @EnableConfigurationProperties 어노테이션에 해당 클래스를 등록해주면 됩니다.

### 4.2. @ConfigurationComponentScan

```java
@ConfigurationPropertiesScan
@Configuration
public class MyConfig {}
```

@EnableConfigurationProperties 어노테이션을 사용하면 설정파일이 늘어날 때마다 등록해줘야하는 불편함이 있습니다. 이러한 불편함을 해소하기 위한 방법으론 @ConfigurationPropertiesScan을 사용하면 됩니다! 기본적으로 해당 어노테이션이 붙은 클래스의 패키지를 스캔하기 때문에 다른 위치에 있다면 아래와 같이 추가해 주시면 됩니다.

```java
@ConfigurationPropertiesScan({ "com.example.app", "com.example.another" })
@Configuration
public class MyConfig {}
```

## 번외 -  @ConstructorBinding 테스트 시 주의할 점

```java
@SpringBootTest(classes = {AppV3Config.class, MyServiceProperty.class})
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
```

위 테스트는 왠지 통과해야 할 것 같은데.. 하지만 실행해보면?

```java
Failed to load ApplicationContext for [WebMergedContextConfiguration@3d49fd31 testClass = me.iseunghan.configurationproperty.config.v3_use_constructor.MyServicePropertyTest, locations = [], classes = [me.iseunghan.configurationproperty.config.v3_use_constructor.AppV3Config, me.iseunghan.configurationproperty.config.v3_use_constructor.MyServiceProperty], contextInitializerClasses = [], activeProfiles = [], propertySourceDescriptors = [], propertySourceProperties = ["org.springframework.boot.test.context.SpringBootTestContextBootstrapper=true"], contextCustomizers = [org.springframework.boot.test.autoconfigure.actuate.observability.ObservabilityContextCustomizerFactory$DisableObservabilityContextCustomizer@1f, org.springframework.boot.test.autoconfigure.properties.PropertyMappingContextCustomizer@0, org.springframework.boot.test.autoconfigure.web.servlet.WebDriverContextCustomizer@10cf09e8, org.springframework.boot.test.context.filter.ExcludeFilterContextCustomizer@6bca7e0d, org.springframework.boot.test.json.DuplicateJsonObjectContextCustomizerFactory$DuplicateJsonObjectContextCustomizer@19835e64, org.springframework.boot.test.mock.mockito.MockitoContextCustomizer@0, org.springframework.boot.test.web.client.TestRestTemplateContextCustomizer@6c0d9d86, org.springframework.boot.test.context.SpringBootTestAnnotation@c8127d7e], resourceBasePath = "src/main/webapp", contextLoader = org.springframework.boot.test.context.SpringBootContextLoader, parent = null]
java.lang.IllegalStateException: Failed to load ApplicationContext for [WebMergedContextConfiguration@3d49fd31 testClass = me.iseunghan.configurationproperty.config.v3_use_constructor.MyServicePropertyTest, locations = [], classes = [me.iseunghan.configurationproperty.config.v3_use_constructor.AppV3Config, me.iseunghan.configurationproperty.config.v3_use_constructor.MyServiceProperty], contextInitializerClasses = [], activeProfiles = [], propertySourceDescriptors = [], propertySourceProperties = ["org.springframework.boot.test.context.SpringBootTestContextBootstrapper=true"], contextCustomizers = [org.springframework.boot.test.autoconfigure.actuate.observability.ObservabilityContextCustomizerFactory$DisableObservabilityContextCustomizer@1f, org.springframework.boot.test.autoconfigure.properties.PropertyMappingContextCustomizer@0, org.springframework.boot.test.autoconfigure.web.servlet.WebDriverContextCustomizer@10cf09e8, org.springframework.boot.test.context.filter.ExcludeFilterContextCustomizer@6bca7e0d, org.springframework.boot.test.json.DuplicateJsonObjectContextCustomizerFactory$DuplicateJsonObjectContextCustomizer@19835e64, org.springframework.boot.test.mock.mockito.MockitoContextCustomizer@0, org.springframework.boot.test.web.client.TestRestTemplateContextCustomizer@6c0d9d86, org.springframework.boot.test.context.SpringBootTestAnnotation@c8127d7e], resourceBasePath = "src/main/webapp", contextLoader = org.springframework.boot.test.context.SpringBootContextLoader, parent = null]
...
Caused by: org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'myServiceProperty': Unsatisfied dependency expressed through constructor parameter 0: No qualifying bean of type 'boolean' available: expected at least 1 bean which qualifies as autowire candidate. Dependency annotations: {}
...
```

`No qualifying bean of type 'boolean' available` .. 예?

`private final boolean enabled` 필드를 빈이라고 착각하고 찾다가 실패한 것으로 추정됩니다.

공식문서를 찾아보니 다음과 같이 친절하게 적어놨습니다.

> To use constructor binding the class must be enabled using `@EnableConfigurationProperties` or configuration property scanning. You cannot use constructor binding with beans that are created by the regular Spring mechanisms (for example `@Component` beans, beans created by using `@Bean`methods or beans loaded by using `@Import`)
>

@Import와 같이 빈을 로드하면, ConstructorBinding을 사용할 수 없다고 친절하게 알려줬네요.. ㅎㅎ

SpringbBootTest(classes={})가 @Import 처럼 동작하여서 그런 것 같습니다.

### TestConfig를 만들어서 테스트!

해당 에러를 해결하기 위해 테스트용 Config를 생성하여 ComponentScan을 v3에 대해서만 지정해주고 테스트에서는 해당 Config만 로드해서 돌려보겠습니다.

```java
@ComponentScan(basePackages = {"me.iseunghan.configurationproperty.config.v3_use_constructor"})
@Configuration
public class TestV3Config {}

@SpringBootTest(classes = {TestV3Config.class})
class MyServicePropertyTest {
	...
}
```

위와 같이 테스트를 다시 해보면..?!

!https://raw.githubusercontent.com/iseunghan/iseunghan-Lab/fb18932941f11cd53732abacfd6aeeb5ece3b863/configurationProperty/img.png

정상적으로 테스트가 성공하는 것을 확인할 수 있습니다!

## REFERENCES

---

[Core Features](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config.typesafe-configuration-properties)