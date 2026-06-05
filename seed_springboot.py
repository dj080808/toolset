"""为 Spring Boot 技术栈填充知识笔记 + 常见面试题"""
from db import get_db

NOTES = [
    (
        "Spring Boot 的历史与发展历程",
        """## Spring Boot 诞生的背景

在 Spring Boot 出现之前（2013 年以前），Spring 框架虽然是 Java 企业开发的事实标准，但存在严重的**"配置地狱"**问题：

1. **XML 配置灾难**：一个简单的 Web 项目需要上百行 XML（web.xml、applicationContext.xml、spring-mvc.xml、mybatis-config.xml...）
2. **依赖版本黑洞**：手动管理几十个依赖的版本兼容性，稍有不慎就出现 ClassNotFoundException
3. **部署繁琐**：需要外置 Tomcat，war 包方式部署，开发和部署环境不一致

## 诞生的故事

- **2012 年**：Spring 团队内部讨论"如何让 Spring 更简单"，提出"约定优于配置"的理念
- **2013 年 10 月**：Spring Boot 在 SpringOne 大会上首次亮相，演示了一个"5 分钟创建一个 Spring Web 应用"的 Demo
- **2014 年 4 月**：Spring Boot **v1.0.0** 正式发布，彻底改变了 Java 开发的体验

## 关键版本演进

| 版本 | 时间 | 重大变更 |
|------|------|----------|
| **1.0** | 2014.04 | 首个 GA，自动配置、Starter、Actuator 三大核心特性就位 |
| **1.2** | 2014.12 | 引入 `@SpringBootApplication` 注解，替代三个注解 |
| **1.5** | 2017.01 | 最后一个 1.x 版本，广泛用于生产 |
| **2.0** | 2018.03 | 基于 Spring Framework 5，引入 WebFlux 响应式支持，Java 8+ |
| **2.3** | 2020.05 | 引入 Docker 分层构建支持（`spring-boot:build-image`）|
| **2.4** | 2020.11 | 配置文件大改：`spring.profiles` 废弃，引入 `spring.config.activate.on-profile` |
| **2.7** | 2022.05 | 最后一个 2.x 系列，关键垫脚石版本（兼容 javax + jakarta）|
| **3.0** | 2022.11 | Java 17 基线，Jakarta EE 9+（包名 `javax.*` → `jakarta.*`），AOT 编译 |
| **3.2** | 2023.11 | 虚拟线程（Virtual Threads）正式支持，RestClient 替代 RestTemplate |
| **3.4** | 2024.12 | Spring Boot 10 周年，持续增强 Native Image 和云原生支持 |

## 为什么 Spring Boot 能火？

1. **解决真实痛点**：每个 Java 开发者都被 XML 配置折磨过，Spring Boot 对症下药
2. **生态捆绑**：Spring 早已是 Java 领域的王者，Boot 是 Spring 的"官方快车道"
3. **微服务浪潮**：2014-2016 年微服务概念大火，Spring Boot 天生适合微服务
4. **文档质量**：Spring 的文档一直是开源项目的标杆，Boot 继承了这一传统
5. **社区运营**：SpringOne、Spring I/O、Spring Tips 视频系列，持续输出高质量内容

## Spring Boot 的"精神继承"

Spring Boot 的很多思想继承自：
- **Ruby on Rails**（2004）——约定优于配置，脚手架生成
- **Grails**（2006）——Groovy on Spring，Spring 生态的"快速开发框架"
- **Dropwizard**（2011）——Java 的轻量级 REST 框架，fat jar 部署

> 有趣的是：Spring Boot 的设计领导者 Phil Webb 和 Dave Syer 都曾深入研究过 Rails 和 Grails，把他们的经验带回了 Spring 生态。""",
        "历史,演进,版本,起源,里程碑",
    ),
    (
        "Spring Boot 核心原理：自动配置与起步依赖",
        """## Spring Boot 解决的核心问题

Spring Boot 不是新框架，而是 **Spring 的快速开发脚手架**，解决三个核心痛点：

1. **繁琐的 XML/Java 配置** → 自动配置
2. **依赖版本冲突** → 起步依赖（Starter）
3. **应用部署麻烦** → 内嵌容器

## 自动配置（Auto-Configuration）

```
@SpringBootApplication
    ├── @SpringBootConfiguration   → @Configuration（标记配置类）
    ├── @EnableAutoConfiguration   → 自动配置的入口
    └── @ComponentScan             → 组件扫描
```

`@EnableAutoConfiguration` 的核心流程：

```
1. AutoConfigurationImportSelector
2. 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
3. 加载所有自动配置类（如 DataSourceAutoConfiguration）
4. 每个配置类上都有 @ConditionalOnXxx 条件注解
5. 条件满足 → 配置生效，条件不满足 → 跳过
```

## 条件注解体系（关键）

| 注解 | 作用 | 示例 |
|------|------|------|
| `@ConditionalOnClass` | classpath 有某个类时生效 | 有 `DataSource` → 自动配数据源 |
| `@ConditionalOnMissingBean` | 容器中没有某个 Bean 时生效 | 用户没定义 `DataSource` → 用默认 |
| `@ConditionalOnProperty` | 配置文件中某属性=某值时生效 | `spring.datasource.url` 存在 → 配数据源 |
| `@ConditionalOnBean` | 容器中有某个 Bean 时生效 | 有 `DataSource` → 配 `JdbcTemplate` |
| `@ConditionalOnWebApplication` | 是 Web 应用时生效 | Web 环境 → 配 DispatcherServlet |

## 起步依赖（Starter）

Starter 是一组依赖的聚合，解决"引什么、引哪个版本"的问题：

```
spring-boot-starter-web
    ├── spring-boot-starter（核心）
    ├── spring-boot-starter-tomcat（内嵌 Tomcat）
    ├── spring-webmvc（Spring MVC）
    └── jackson-databind（JSON 序列化）
```

**命名规范**：
- **官方**：`spring-boot-starter-xxx`（如 `spring-boot-starter-data-redis`）
- **第三方**：`xxx-spring-boot-starter`（如 `mybatis-spring-boot-starter`）""",
        "自动配置,starter,原理,核心,条件注解",
    ),
    (
        "@SpringBootApplication 注解深度解析",
        """## @SpringBootApplication 的三合一结构

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration      // ①
@EnableAutoConfiguration      // ②
@ComponentScan(               // ③
    excludeFilters = {
        @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
        @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class)
    }
)
public @interface SpringBootApplication {
    // 可配置属性...
    Class<?>[] exclude() default {};  // 排除特定自动配置类
    String[] excludeName() default {};
    String[] scanBasePackages() default {};  // 扫描包路径
    Class<?>[] scanBasePackageClasses() default {};
}
```

### ① @SpringBootConfiguration

本质就是 `@Configuration`，标记这是一个 Spring 配置类。多了一层封装方便语义化。

### ② @EnableAutoConfiguration

```java
@AutoConfigurationPackage  // 将主类所在包注册为"自动配置包"
@Import(AutoConfigurationImportSelector.class)  // 核心：导入自动配置类
public @interface EnableAutoConfiguration {}
```

**AutoConfigurationImportSelector 工作原理**：

```
1. getAutoConfigurationEntry()
2. → getCandidateConfigurations()  读取 spring.factories 或 .imports 文件
3. → removeDuplicates()            去重
4. → getExclusions()               排除 exclude 指定的类
5. → filter(configurations)        按 @Conditional 过滤
6. → 最终返回需要生效的自动配置类列表
```

### ③ @ComponentScan

默认扫描**主类所在包及子包**。这就是为什么主类要放在根目录——这样所有组件都能被扫描到。

> **关键约定**：主类应放在 `com.example`，所有业务代码在 `com.example.*` 下，这样不用显式配置扫描路径。

### 排除自动配置

```java
// 排除 DataSource 自动配置
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class Application { ... }
```

或通过配置：
```yaml
spring:
  autoconfigure:
    exclude:
      - org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```""",
        "注解,SpringBootApplication,源码,三合一",
    ),
    (
        "Spring Boot 启动流程全解析",
        """## SpringApplication.run() 全流程

```java
SpringApplication.run(Application.class, args);
```

### 完整启动流程（8 步）

```
① 创建 SpringApplication 实例
    ├── 推断应用类型（SERVLET / REACTIVE / NONE）
    ├── 加载 ApplicationContextInitializer
    └── 加载 ApplicationListener

② 启动 SpringApplicationRunListeners
    → 发布 ApplicationStartingEvent

③ 准备 Environment
    ├── 解析命令行参数
    ├── 加载配置文件（application.yml/properties）
    ├── 激活 profile
    └── 发布 ApplicationEnvironmentPreparedEvent

④ 创建 ApplicationContext
    ├── Servlet 环境 → AnnotationConfigServletWebServerApplicationContext
    └── Reactive 环境 → AnnotationConfigReactiveWebServerApplicationContext

⑤ 准备 Context
    ├── 设置 Environment
    ├── 执行 ApplicationContextInitializer
    └── 发布 ApplicationContextInitializedEvent

⑥ 刷新 Context（核心）
    ├── 解析配置类
    ├── 扫描 Bean
    ├── 执行自动配置（AutoConfigurationImportSelector）
    ├── 实例化单例 Bean
    └── 启动内嵌 WebServer

⑦ 刷新后回调
    ├── 执行 CommandLineRunner
    ├── 执行 ApplicationRunner
    └── 发布 ApplicationReadyEvent

⑧ 返回 Context，应用启动完成
```

## 关键源码位置

| 类 | 职责 |
|----|------|
| `SpringApplication` | 启动主流程编排 |
| `SpringApplicationRunListeners` | 事件广播 |
| `AutoConfigurationImportSelector` | 加载自动配置类 |
| `ConfigurationClassParser` | 解析 @Configuration 类 |
| `ServletWebServerApplicationContext` | 创建内嵌 Tomcat |

## 自定义启动逻辑

两种方式在启动后执行代码：

```java
// 方式 1：ApplicationRunner（推荐，参数更丰富）
@Component
public class MyRunner implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) {
        System.out.println("应用启动完成: " + args.getOptionNames());
    }
}

// 方式 2：CommandLineRunner（参数简单）
@Component
public class MyCommandRunner implements CommandLineRunner {
    @Override
    public void run(String... args) {
        System.out.println("应用启动完成");
    }
}
```

## 启动失败分析

Spring Boot 2.0+ 内置了 **FailureAnalyzer** 机制：

```
启动失败 → 遍历 FailureAnalyzer 列表
         → 匹配到的 Analyzer 给出诊断信息
         → 如 PortInUseFailureAnalyzer："端口 8080 被占用"
```""",
        "启动流程,SpringApplication,源码,生命周期,事件",
    ),
    (
        "Spring Boot 配置管理与外部化配置",
        """## 配置优先级（从高到低，共 17 级）

Spring Boot 的配置优先级非常精细，以下是核心级别：

```
1.  命令行参数                    --server.port=9090
2.  JNDI 属性                    java:comp/env
3.  System.getProperties()       系统属性
4.  OS 环境变量                   SERVER_PORT=9090
5.  RandomValuePropertySource    random.* 随机值
6.  jar 包外部的 application-{profile}.yml
7.  jar 包内部的 application-{profile}.yml
8.  jar 包外部的 application.yml
9.  jar 包内部的 application.yml
10. @PropertySource 注解
11. SpringApplication.setDefaultProperties()
```

## application.yml vs application.properties

```yaml
# YAML（推荐，层次清晰）
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/db
    username: root
  profiles:
    active: dev
```

```properties
# Properties（简单，适合单值）
spring.datasource.url=jdbc:mysql://localhost:3306/db
spring.datasource.username=root
spring.profiles.active=dev
```

## Profile 多环境配置

```
application.yml              # 公共配置
application-dev.yml          # 开发环境
application-test.yml         # 测试环境
application-prod.yml         # 生产环境
```

激活方式（优先级从高到低）：
```bash
# 1. 命令行
java -jar app.jar --spring.profiles.active=prod

# 2. 环境变量
export SPRING_PROFILES_ACTIVE=prod

# 3. application.yml
spring.profiles.active=prod
```

## 配置绑定

```java
// 方式 1：@Value（单体值）
@Value("${app.name}")
private String appName;

// 方式 2：@ConfigurationProperties（批量绑定，推荐）
@ConfigurationProperties(prefix = "app")
@Component
public class AppConfig {
    private String name;
    private int timeout;
    private List<String> servers;
    // getter/setter...
}
```

```yaml
app:
  name: myapp
  timeout: 3000
  servers:
    - server1
    - server2
```

> **@Value vs @ConfigurationProperties**：单个值用 @Value，批量绑定用 @ConfigurationProperties，后者支持 Relaxed Binding（松散绑定）和 JSR-303 校验。""",
        "配置,优先级,profile,多环境,ConfigurationProperties",
    ),
    (
        "Spring Boot Actuator 监控体系",
        """## Actuator 是什么

Actuator 是 Spring Boot 内置的**应用监控和运维工具**，提供生产就绪特性。

## 核心端点

| 端点 | 说明 | 默认暴露 |
|------|------|----------|
| `/actuator/health` | 健康检查（应用状态 + DB/Redis 等组件）| ✅ Web |
| `/actuator/info` | 应用信息（版本、描述）| ✅ Web |
| `/actuator/metrics` | 指标汇总（JVM、HTTP、DB 连接等）| ❌ |
| `/actuator/env` | 环境变量和配置属性 | ❌ |
| `/actuator/loggers` | 查看和修改日志级别 | ❌ |
| `/actuator/mappings` | 所有 RequestMapping 信息 | ❌ |
| `/actuator/beans` | 所有 Bean 列表 | ❌ |
| `/actuator/threaddump` | 线程快照 | ❌ |
| `/actuator/heapdump` | 堆转储文件下载 | ❌ |
| `/actuator/prometheus` | Prometheus 格式指标（需引入 micrometer）| ❌ |

## 配置暴露

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics  # 暴露指定端点
        # include: "*"                 # 暴露全部（谨慎！）
      base-path: /actuator
  endpoint:
    health:
      show-details: always  # 显示健康详情
```

## 自定义健康检查

```java
@Component
public class MyHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        // 检查某个外部依赖
        boolean isHealthy = checkExternalService();
        if (isHealthy) {
            return Health.up()
                .withDetail("service", "available")
                .build();
        }
        return Health.down()
            .withDetail("service", "unavailable")
            .build();
    }
}
```

## 与 Micrometer 集成

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

引入后访问 `/actuator/prometheus` 即可获得 Prometheus 格式指标，接入 Grafana 做可视化。""",
        "Actuator,监控,端点,健康检查,指标",
    ),
    (
        "Spring Boot Starter 自定义开发",
        """## 自定义 Starter 的开发规范

### 命名规范

- **官方**：`spring-boot-starter-{模块名}`
- **第三方/自定义**：`{模块名}-spring-boot-starter`

### Starter 项目结构

```
my-spring-boot-starter/
├── pom.xml
├── src/main/java/com/example/
│   ├── MyAutoConfiguration.java    # 自动配置类
│   ├── MyProperties.java           # 配置属性类
│   └── MyService.java              # 核心服务类
└── src/main/resources/
    └── META-INF/
        └── spring/
            └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

### 步骤详解

**1. 配置属性类**

```java
@ConfigurationProperties(prefix = "my.starter")
public class MyProperties {
    private boolean enabled = true;
    private String url = "http://localhost:8080";
    private int timeout = 5000;
    // getter/setter...
}
```

**2. 核心服务类**

```java
public class MyService {
    private final MyProperties properties;

    public MyService(MyProperties properties) {
        this.properties = properties;
    }

    public void execute() {
        System.out.println("Connecting to " + properties.getUrl());
    }
}
```

**3. 自动配置类**

```java
@Configuration
@EnableConfigurationProperties(MyProperties.class)  // 激活属性类
@ConditionalOnProperty(prefix = "my.starter", name = "enabled", havingValue = "true", matchIfMissing = true)
@ConditionalOnClass(MyService.class)                // classpath 有该类才生效
public class MyAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MyService myService(MyProperties properties) {
        return new MyService(properties);
    }
}
```

**4. 注册自动配置**

`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`：
```
com.example.MyAutoConfiguration
```

> **Spring Boot 2.x vs 3.x**：2.x 用 `META-INF/spring.factories` 中的 `org.springframework.boot.autoconfigure.EnableAutoConfiguration` key，3.x 改为 `.imports` 文件。

### 条件注解的最佳实践

- 用 `@ConditionalOnClass` 检查核心依赖是否存在
- 用 `@ConditionalOnMissingBean` 允许用户覆盖默认 Bean
- 用 `@ConditionalOnProperty` 提供开关
- 用 `@ConditionalOnWebApplication` 区分 Web 和非 Web 场景""",
        "Starter,自定义,自动配置,开发规范",
    ),
    (
        "Spring Boot 嵌入式容器：Tomcat/Jetty/Undertow",
        """## 三种嵌入式容器对比

| 特性 | Tomcat | Jetty | Undertow |
|------|--------|-------|----------|
| **默认** | ✅ Spring Boot 默认 | | |
| **启动速度** | 中等 | 快 | 最快 |
| **内存占用** | 中等 | 小 | 最小 |
| **并发模型** | 线程池（BIO/NIO）| 线程池（NIO）| 事件驱动（NIO）|
| **HTTP/2** | ✅ 原生支持 | ✅ | ✅ |
| **适用场景** | 通用场景 | 嵌入式/轻量场景 | 高并发/低资源场景 |
| **Servlet 版本** | 6.0 (Boot 3.x) | 6.0 | 不直接支持 |

## 切换容器

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <!-- 排除 Tomcat -->
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<!-- 使用 Undertow -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>
```

## 定制 Tomcat

```java
@Component
public class TomcatCustomizer implements WebServerFactoryCustomizer<TomcatServletWebServerFactory> {
    @Override
    public void customize(TomcatServletWebServerFactory factory) {
        factory.setPort(9090);
        factory.addConnectorCustomizers(connector -> {
            // 开启 APR（需要 tomcat-native 库）
            connector.setProperty("relaxedQueryChars", "|{}[]");
        });
    }
}
```

或通过配置：
```yaml
server:
  port: 8080
  tomcat:
    max-connections: 10000
    threads:
      max: 200
      min-spare: 10
    accept-count: 100
    connection-timeout: 30000
```""",
        "Tomcat,Jetty,Undertow,容器,嵌入式",
    ),
    (
        "Spring Boot 与 Spring Cloud 的关系",
        """## 层次关系

```
┌────────────────────────────────────────┐
│          Spring Cloud                   │  ← 微服务治理（注册、配置、网关、熔断...）
│  ┌──────────────────────────────────┐  │
│  │        Spring Boot               │  │  ← 快速开发脚手架（自动配置、Starter、Actuator）
│  │  ┌────────────────────────────┐  │  │
│  │  │      Spring Framework      │  │  │  ← IoC 容器、AOP、MVC、事务...
│  │  └────────────────────────────┘  │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

## 核心区别

| 维度 | Spring Framework | Spring Boot | Spring Cloud |
|------|-----------------|-------------|-------------|
| **定位** | Java 企业开发基础框架 | 快速开发脚手架 | 微服务治理工具集 |
| **核心能力** | IoC/DI、AOP、MVC、事务 | 自动配置、Starter、Actuator | 注册发现、配置、网关、熔断 |
| **配置方式** | XML/Java Config | application.yml + 自动配置 | Bootstrap 上下文 + 自动配置 |
| **部署** | 外置 Servlet 容器 | 内嵌容器（fat jar）| 内嵌容器 + 注册中心 |

## 版本对应关系

```
Spring Boot 3.x  →  Spring Cloud 2022.x+ (Kilburn/Leyton...)
Spring Boot 2.7  →  Spring Cloud 2021.x (Jubilee)
Spring Boot 2.6  →  Spring Cloud 2021.0.0
Spring Boot 2.5  →  Spring Cloud 2020.0.x (Ilford)
Spring Boot 2.4  →  Spring Cloud 2020.0.0
```

> **重要**：Spring Boot 3.x 要求 Java 17+，基于 Jakarta EE 9+（包名从 `javax.*` → `jakarta.*`），这是迁移时最大的变更点。

## Spring Cloud 的依赖方式

```xml
<!-- BOM 方式管理版本（推荐）-->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>2023.0.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

引入 BOM 后，Spring Cloud 组件的版本统一由 BOM 管理，不需要手动指定。""",
        "Spring Cloud,关系,层次,版本,对比",
    ),
]

INTERVIEWS = [
    (
        "Spring Boot 是怎么来的？和 Spring Framework 是什么关系？",
        """## 参考答案

### 一句话关系

**Spring Boot 是 Spring Framework 的"快速启动器"，不是替代品，而是建立在 Spring 基础上的脚手架。**

### Spring 的历史演进

```
2002: Rod Johnson 出版《Expert One-on-One J2EE Design and Development》
      → 批判 EJB 的臃肿，提出轻量级 IoC 容器思想

2004: Spring Framework 1.0 发布
      → XML 配置的时代，一个 Bean 一行 <bean> 标签

2007: Spring 2.5 → 引入 @Autowired 注解，开始简化配置

2009: Spring 3.0 → Java Config 初现（@Configuration、@Bean）

2014: Spring Boot 1.0 正式发布
      → "约定优于配置" + 自动配置 + 内嵌容器
      → 让 Spring 开发从"配置驱动"变成"代码驱动"
```

### Spring Boot 解决了什么？

在学校 / 自学 Spring 时，你可能经历过：
1. 项目里 5+ 个 XML 文件，互相 import
2. 配个数据源要写 30 行 XML
3. 依赖版本不兼容，各种 ClassNotFoundException
4. 本地开发用 Tomcat 8，服务器上是 Tomcat 7 → 各种兼容问题
5. 每个项目都要 copy 一遍基础配置

Spring Boot 解决这些的方式：
- 自动配置：不写配置 = 用默认，写了 = 覆盖默认
- Starter：一个依赖替代十几个依赖
- 内嵌容器：打出来就能跑，`java -jar xx.jar`

### 面试加分点

Spring Boot 不是新技术，它做的三件事 Spring Framework 一直都支持：
- 自动配置 = `@Configuration` + `@Conditional` + `@Bean`
- Starter = Maven/Gradle 的 `pom` 依赖传递
- 内嵌容器 = 把 Tomcat 当成一个 jar 包嵌入

> Spring Boot 的创新不在于技术本身，在于**把正确的事情做成了默认**。""",
        "历史,关系,演进,起源",
    ),
    (
        "Spring Boot 的自动配置原理是什么？如何实现一个自动配置？",
        """## 参考答案

### 自动配置原理

Spring Boot 自动配置的核心流程：

```
@EnableAutoConfiguration
    │
    └→ @Import(AutoConfigurationImportSelector.class)
            │
            └→ selectImports()
                    │
                    ├→ ① 读取 spring-boot-autoconfigure 下的
                    │     META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
                    │     （3.x）/ spring.factories（2.x）
                    │
                    ├→ ② 加载所有候选自动配置类（~150+ 个）
                    │
                    ├→ ③ 对每个配置类，根据 @ConditionalOnXxx 条件过滤
                    │     - @ConditionalOnClass：classpath 有对应的类才生效
                    │     - @ConditionalOnMissingBean：用户没定义才用默认
                    │     - @ConditionalOnProperty：配了对应属性才生效
                    │
                    └→ ④ 条件满足的配置类生效，向容器注册对应的 Bean
```

以 `DataSourceAutoConfiguration` 为例：
```java
@AutoConfiguration
@ConditionalOnClass({DataSource.class, EmbeddedDatabaseType.class})  // ← classpath 有这些类
@EnableConfigurationProperties(DataSourceProperties.class)
@Import({DataSourcePoolMetadataProvidersConfiguration.class, ...})
public class DataSourceAutoConfiguration {

    @Configuration
    @ConditionalOnProperty(prefix = "spring.datasource", name = "url")  // ← 配了 url 才生效
    static class PooledDataSourceConfiguration {
        @Bean
        @ConditionalOnMissingBean  // ← 用户没定义 DataSource 才用这个
        DataSource dataSource(DataSourceProperties properties) {
            return properties.initializeDataSourceBuilder().build();
        }
    }
}
```

### 如何实现一个自动配置（完整步骤）

```java
// 1. 定义配置属性
@ConfigurationProperties(prefix = "my.starter")
public class MyProperties {
    private boolean enabled = true;
    private String url;
    // getter/setter
}

// 2. 自动配置类
@AutoConfiguration
@EnableConfigurationProperties(MyProperties.class)
@ConditionalOnClass(SomeService.class)
@ConditionalOnProperty(prefix = "my.starter", name = "enabled", matchIfMissing = true)
public class MyAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public SomeService someService(MyProperties prop) {
        return new SomeService(prop.getUrl());
    }
}

// 3. 注册到 spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

### 面试加分点

自定义 Starter 时的几个实践原则：
- `@ConditionalOnMissingBean` 保证用户能覆盖默认实现
- 不要用 `@AutoConfigureBefore` / `@AutoConfigureAfter` 除非明确知道顺序依赖
- Starter 里**不要做耗时操作**（如建立数据库连接），会拖慢启动速度
- 属性类用 `@ConfigurationProperties` 而非 `@Value`，支持 IDE 提示 + 松散绑定""",
        "自动配置,原理,源码,高频,核心",
    ),
    (
        "Spring Boot 的启动流程是怎样的？SpringApplication.run() 做了什么？",
        """## 参考答案

### 完整启动流程

`SpringApplication.run()` 可以分为 **8 个核心阶段**：

**阶段 1：创建 SpringApplication 实例**
```java
// 推断应用类型
WebApplicationType.deduceFromClasspath()
  → 有 DispatcherServlet → SERVLET
  → 有 DispatcherHandler + 无 DispatcherServlet → REACTIVE
  → 其他 → NONE
```

**阶段 2：发布启动事件 → 加载 Environment**
- 解析命令行参数 → `StandardEnvironment` 中包含 `commandLineArgs`
- 加载 `application.yml` / `application.properties`
- 激活 `spring.profiles.active` 指定的 profile

**阶段 3：创建 ApplicationContext**
- Servlet → `AnnotationConfigServletWebServerApplicationContext`
- Reactive → `AnnotationConfigReactiveWebServerApplicationContext`

**阶段 4：准备 Context**
- 注入 environment
- 执行 `ApplicationContextInitializer`
- 加载主类为配置源

**阶段 5：refresh Context（最核心）**
这是 Spring `AbstractApplicationContext.refresh()` 的标准流程：
```
prepareRefresh() → obtainFreshBeanFactory() → prepareBeanFactory()
→ postProcessBeanFactory() → invokeBeanFactoryPostProcessors()
  → 这里触发 AutoConfigurationImportSelector！
→ registerBeanPostProcessors() → initMessageSource()
→ initApplicationEventMulticaster() → onRefresh()
  → 这里启动内嵌 WebServer（Tomcat）！
→ registerListeners() → finishBeanFactoryInitialization()
  → 实例化所有单例 Bean
→ finishRefresh() → 发布 ContextRefreshedEvent
```

**阶段 6：启动内嵌 WebServer**

**阶段 7：执行 Runner**
```java
// 先 ApplicationRunner，后 CommandLineRunner
// 多个 Runner 可以用 @Order 排序
```

**阶段 8：发布 ApplicationReadyEvent → 返回 Context**

### 面试加分点

**refresh 和 onRefresh 的区别**：
- `refresh()` 是 Spring Framework 的标准容器启动方法
- `onRefresh()` 是 Spring Boot 重写的钩子方法，在这里启动内嵌 Tomcat

**启动过程中哪里会失败**：
- Bean 实例化失败（最常见）
- 端口被占用（`PortInUseException`）
- 自动配置冲突（多个同类型 DataSource Bean）
- 配置文件语法错误（YAML 格式错误最难排查）""",
        "启动流程,SpringApplication,源码,生命周期,高频",
    ),
    (
        "Spring Boot 配置加载的优先级是什么？Profile 如何切换？",
        """## 参考答案

### 配置优先级（从高到低）

Spring Boot 完整配置优先级有 17 级，面试只需记住核心的 6 级：

```
① 命令行参数                          --server.port=9090（最高优先级）
② 操作系统环境变量                     SERVER_PORT=9090
③ application-{profile}.yml (.jar 外部)（如 config/application-prod.yml）
④ application-{profile}.yml (.jar 内部)
⑤ application.yml (.jar 外部)
⑥ application.yml (.jar 内部）（最低优先级）
```

记忆口诀：**命令行 > 环境变量 > jar 外 profile > jar 内 profile > jar 外 > jar 内**

### Profile 多环境

```yaml
# application.yml（公共配置）
server:
  port: 8080
spring:
  profiles:
    active: dev  # 默认激活 dev
---
# application-dev.yml
spring:
  config:
    activate:
      on-profile: dev
  datasource:
    url: jdbc:mysql://localhost:3306/dev_db
---
# application-prod.yml
spring:
  config:
    activate:
      on-profile: prod
  datasource:
    url: jdbc:mysql://prod-server:3306/prod_db
```

激活方式：
```bash
# 1. 命令行（最高优先级）
java -jar app.jar --spring.profiles.active=prod

# 2. 环境变量
export SPRING_PROFILES_ACTIVE=prod

# 3. 代码内（最低优先级）
SpringApplication.setAdditionalProfiles("prod");
```

### yml vs properties 的合并规则

如果有同名配置：
- 优先级高的**覆盖**优先级低的
- **不是 merge**，是整个 key 替换
- `application.yml` 和 `application.properties` 都存在时，**.yml 先加载，.properties 后加载，后者覆盖前者**

### 面试加分点

- **Profile Group**（2.4+）：可以用一个 profile 激活一组
  ```yaml
  spring.profiles.group.production:
    - prod
    - monitoring
    - db-prod
  ```
- **配置加密**：Spring Boot 不自带，需要用 Jasypt 或 Vault
- **配置中心**：生产环境引 Nacos/Apollo 后，远程配置优先级高于本地文件""",
        "配置,优先级,Profile,多环境,高频",
    ),
    (
        "如何自定义一个 Spring Boot Starter？需要注意什么？",
        """## 参考答案

### 自定义 Starter 的完整步骤

**第 1 步：创建项目**

```
my-spring-boot-starter/
├── pom.xml
├── MyAutoConfiguration.java
├── MyProperties.java
└── META-INF/spring/
    └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

**第 2 步：定义属性类**
```java
@ConfigurationProperties(prefix = "my.starter")
public class MyProperties {
    private boolean enabled = true;
    private String url;
    private int timeout = 5000;
}
```

**第 3 步：实现核心服务**
```java
public class MyService {
    public MyService(String url, int timeout) { ... }
    public void doSomething() { ... }
}
```

**第 4 步：编写自动配置**
```java
@AutoConfiguration
@EnableConfigurationProperties(MyProperties.class)
@ConditionalOnClass(MyService.class)
@ConditionalOnProperty(prefix = "my.starter", name = "enabled", matchIfMissing = true)
public class MyAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MyService myService(MyProperties prop) {
        return new MyService(prop.getUrl(), prop.getTimeout());
    }
}
```

**第 5 步：注册**
`AutoConfiguration.imports` 中写配置类全限定名。

### 注意事项

1. **命名规范**：官方用 `spring-boot-starter-xxx`，第三方用 `xxx-spring-boot-starter`
2. **不要执行耗时初始化**：Starter 的自动配置只在容器启动时执行，不要在构造方法里建连接
3. **用 @ConditionalOnMissingBean**：让用户可以覆盖
4. **属性类建议加 @Validated**：支持 JSR-303 校验
5. **不要把自动配置写在业务代码里**：Starter 是独立 jar，通过依赖引入
6. **Boot 3.x 用 .imports 文件，不再是 spring.factories**

### 面试加分点

可以提到 Starter 的两个实际设计案例：
- **动态数据源 Starter**：自动配置里读取 `spring.datasource` 的多数据源配置，动态创建 `DataSource` Bean
- **日志链路追踪 Starter**：用 AOP 在 Controller 层自动注入 `traceId` 到日志 MDC 中""",
        "Starter,自定义,自动配置,规范",
    ),
    (
        "Spring Boot 如何处理跨域（CORS）？有几种方式？",
        """## 参考答案

### 三种跨域处理方式

**方式 1：@CrossOrigin 注解（细粒度）**

```java
// 类级别 → 所有方法生效
@CrossOrigin(origins = "http://localhost:3000", maxAge = 3600)
@RestController
@RequestMapping("/api")
public class UserController {

    // 方法级别 → 优先级更高，可覆盖类级别
    @CrossOrigin(origins = "*")
    @GetMapping("/users")
    public List<User> getUsers() {
        return userService.findAll();
    }
}
```

**方式 2：全局配置（推荐）**

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")       // 路径
                .allowedOrigins("http://localhost:3000")  // 允许的源
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*")
                .allowCredentials(true)       // 允许携带 Cookie
                .maxAge(3600);                // 预检请求缓存
    }
}
```

**方式 3：CorsFilter（原生级别）**

```java
@Bean
public CorsFilter corsFilter() {
    CorsConfiguration config = new CorsConfiguration();
    config.addAllowedOrigin("*");
    config.addAllowedMethod("*");
    config.addAllowedHeader("*");

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return new CorsFilter(source);
}
```

**方式 4：Spring Security 中的跨域**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.cors().configurationSource(corsConfigurationSource())
        .and().csrf().disable()...;
    return http.build();
}
```

### 三种方式的对比

| 方式 | 粒度 | 适用场景 |
|------|------|----------|
| `@CrossOrigin` | 类/方法级 | 只有少数接口需要跨域 |
| `WebMvcConfigurer` | 路径级 | 最常用，灵活配置 |
| `CorsFilter` | 全局 | 需要 Spring Security 配合时 |

### 注意事项

- `allowedOrigins("*")` 和 `allowCredentials(true)` **不能同时使用**
- 携带 Cookie 时必须指定具体 Origin 而非 `*`
- 生产环境不要用 `*`，明确指定允许的域名""",
        "跨域,CORS,Spring Security,配置",
    ),
    (
        "Spring Boot 中 Bean 的生命周期是怎样的？",
        """## 参考答案

### Bean 的完整生命周期

```
① 实例化 Instantiation
    │  构造函数 / 工厂方法创建对象
    ├→ ② 属性赋值 Populate Properties
    │  依赖注入（@Autowired、@Value）
    ├→ ③ Aware 回调
    │  BeanNameAware → BeanFactoryAware → ApplicationContextAware
    ├→ ④ BeanPostProcessor.postProcessBeforeInitialization()
    │  （如 @PostConstruct 的处理器 CommonAnnotationBeanPostProcessor）
    ├→ ⑤ InitializingBean.afterPropertiesSet()
    ├→ ⑥ init-method（@Bean(initMethod = "...")）
    ├→ ⑦ BeanPostProcessor.postProcessAfterInitialization()
    │  （AOP 代理在这里创建！）
    ├→ ⑧ Bean 就绪，可被使用
    │
    │  ... 使用中 ...
    │
    ├→ ⑨ DisposableBean.destroy()
    ├→ ⑩ destroy-method（@Bean(destroyMethod = "...")）
    └→ Bean 销毁
```

### 关键节点解释

**postProcessBeforeInitialization vs postProcessAfterInitialization**

这两个方法是 AOP 的核心：
- `before`：通常做初始化前置处理
- `after`：**AOP 代理在这里生成**——`AbstractAutoProxyCreator` 在这步判断是否需要创建代理

**@PostConstruct vs InitializingBean**
- `@PostConstruct`（javax/jakarta 标准）：通过 `CommonAnnotationBeanPostProcessor` 在 before 阶段调用
- `InitializingBean.afterPropertiesSet()`：在 PostConstruct 之后，init-method 之前
- 执行顺序：`@PostConstruct → afterPropertiesSet() → initMethod`

### 如何干预 Bean 生命周期

```java
// 方式 1：注解（推荐）
@PostConstruct
public void init() { ... }
@PreDestroy
public void destroy() { ... }

// 方式 2：实现接口
@Component
public class MyService implements InitializingBean, DisposableBean {
    @Override
    public void afterPropertiesSet() { ... }
    @Override
    public void destroy() { ... }
}

// 方式 3：@Bean 指定
@Bean(initMethod = "init", destroyMethod = "destroy")
public MyService myService() { return new MyService(); }

// 方式 4：BeanPostProcessor（最高级）
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) {
        // 所有 Bean 初始化前都会经过这里
        return bean;
    }
}
```""",
        "Bean,生命周期,PostConstruct,Aware,BeanPostProcessor",
    ),
    (
        "Spring Boot 如何实现优雅停机？",
        """## 参考答案

### 优雅停机配置

```yaml
server:
  shutdown: graceful  # 开启优雅停机（默认 immediate）

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # 等待时间
```

### 优雅停机的流程

```
① 收到 SIGTERM 信号（kill 命令 / K8s preStop）
② 应用标记为不可用
③ WebServer 停止接收新请求
④ 等待正在处理的请求完成（最多 timeout-per-shutdown-phase）
⑤ 销毁 Bean（@PreDestroy）
⑥ 关闭连接池（数据源、Redis 等）
⑦ 关闭 WebServer
⑧ Spring 容器关闭
⑨ 应用进程退出
```

### 实现方式

```java
// 1. 监听 ContextClosedEvent
@Component
public class GracefulShutdown implements ApplicationListener<ContextClosedEvent> {
    @Override
    public void onApplicationEvent(ContextClosedEvent event) {
        // 自定义关闭逻辑
        System.out.println("开始优雅停机...");
    }
}

// 2. @PreDestroy（更简单）
@Component
public class MyService {
    @PreDestroy
    public void cleanup() {
        // 释放资源
    }
}
```

### K8s 中的优雅停机

```yaml
# Deployment
spec:
  template:
    spec:
      containers:
        - name: app
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]  # ← 关键：延迟关闭
      terminationGracePeriodSeconds: 60  # 最长等待时间
```

K8s 的终止流程：
```
① Pod 标记为 Terminating → 从 Service Endpoint 移除
② 执行 preStop Hook（如果有）
③ 发送 SIGTERM 给容器（Spring Boot 开始 graceful shutdown）
④ 等待 terminationGracePeriodSeconds
⑤ 未退出 → 发送 SIGKILL 强制终止
```

> **关键**：`server.shutdown=graceful` 和 `preStop sleep 15` 配合使用，确保从 Service 摘除到应用真正停止之间有足够的"排水"时间。""",
        "优雅停机,graceful,shutdown,K8s,preStop",
    ),
    (
        "Spring Boot 3.x 相比 2.x 有哪些重大变更？",
        """## 参考答案

### 核心变更一览

| 变更项 | 2.x | 3.x |
|--------|-----|-----|
| **Java 基线** | Java 8（2.x）→ 17（3.0+）| Java 17+ 强制要求 |
| **Jakarta EE** | `javax.*` 包名 | `jakarta.*` 包名 |
| **Spring Framework** | 5.x | 6.x |
| **自动配置注册** | `spring.factories` | `AutoConfiguration.imports` |
| **可观测性** | Spring Cloud Sleuth | Micrometer Tracing |
| **AOT 编译** | 不支持 | ✅ Native Image 支持 |
| **虚拟线程** | 不支持 | ✅ Project Loom 支持（3.2+）|
| **HTTP 客户端** | RestTemplate（标记废弃）| HTTP Interface（声明式）|
| **问题与答案（ProblemDetail）** | 无 | ✅ RFC 7807 标准错误响应 |
| **可执行 Jar** | Fat Jar | 更高效的 SBOM + CDS |

### 三大最影响迁移的变更

**1. javax → jakarta（最痛苦）**

所有 Java EE 的包名从 `javax.*` 变为 `jakarta.*`：
```java
// 2.x
import javax.servlet.http.HttpServletRequest;
import javax.persistence.Entity;

// 3.x
import jakarta.servlet.http.HttpServletRequest;
import jakarta.persistence.Entity;
```

影响范围：Servlet、JPA、Validation、Mail、Transaction 等。

**2. 自动配置注册方式变更**

```
2.x: META-INF/spring.factories → org.springframework.boot.autoconfigure.EnableAutoConfiguration=com.xxx.Xxx
3.x: META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports → com.xxx.Xxx
```

**3. 可观测性方案变更**
- 2.x：Sleuth + Brave + Zipkin
- 3.x：Micrometer Tracing（统一指标+追踪），Sleuth 已归档

### 新特性亮点
- **GraalVM Native Image**：编译为二进制，毫秒级启动
- **虚拟线程（3.2+）**：`spring.threads.virtual.enabled=true` 开启
- **声明式 HTTP 客户端**：`@HttpExchange` 替代 RestTemplate

### 面试加分点

迁移经验：**先升级 2.7 → 3.0，不要跳版本**。2.7 是关键垫脚石版本，保持了 `javax.*` 的同时提供了 Jakarta EE 9 的兼容层，可以先测试 Jakarta 兼容性再切到 3.x 彻底替换。""",
        "3.x,2.x,迁移,变更,Jakarta",
    ),
]


def seed():
    db = get_db()
    row = db.execute("SELECT id FROM stack WHERE name = 'Spring Boot'").fetchone()
    if not row:
        print("Spring Boot stack not found!")
        return
    sid = row["id"]

    db.execute("DELETE FROM entry WHERE stack_id = ?", (sid,))

    for title, content, tags in NOTES:
        db.execute(
            "INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?, ?, ?, ?, 'note')",
            (sid, title, content, tags),
        )

    for title, content, tags in INTERVIEWS:
        db.execute(
            "INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?, ?, ?, ?, 'interview')",
            (sid, title, content, tags),
        )

    db.commit()
    db.close()
    print(f"Spring Boot: {len(NOTES)} notes + {len(INTERVIEWS)} interview questions inserted")


if __name__ == "__main__":
    seed()
