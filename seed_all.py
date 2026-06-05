"""一次性填充所有未填的技术栈：历史、原理、面试题"""
from db import get_db


# ====================================================================
# P1: OpenFeign + LoadBalancer
# ====================================================================

FEIGN_NOTES = [
    (
        "OpenFeign 的历史与演进",
        """## 起源

OpenFeign 的前身是 **Netflix Feign**，由 Netflix 在 2013 年开源，定位是"编写 Java HTTP 客户端像写接口一样简单"。

2016 年 Netflix 将 Feign 捐赠给 **OpenFeign 社区**（移至 GitHub `OpenFeign/feign` 组织），改名 OpenFeign，脱离 Netflix 生态独立发展。

Spring Cloud 团队看到 Feign 的价值，2016 年推出 **Spring Cloud OpenFeign**，将 Feign 与 Spring MVC 注解深度整合——Controller 和 Feign 接口可以复用同一个 DTO 和注解体系。

## 关键演进

| 时间 | 事件 |
|------|------|
| 2013 | Netflix Feign 开源 |
| 2016 | 移交 OpenFeign 社区，独立发展 |
| 2016 | Spring Cloud OpenFeign 发布，集成 Ribbon |
| 2020 | Spring Cloud Hoxton → 默认使用 LoadBalancer 替代 Ribbon |
| 2022+ | Feign 支持 HTTP/2、gRPC、Spring Boot 3.x |

## 为什么用 Feign

在 Feign 之前，Java 调用 HTTP 接口要这样：
```java
RestTemplate restTemplate = new RestTemplate();
String result = restTemplate.getForObject("http://user-service/users/" + id, String.class);
```

用 Feign 之后：
```java
@FeignClient(name = "user-service")
public interface UserClient {
    @GetMapping("/users/{id}")
    UserDTO getUser(@PathVariable("id") Long id);
}
```

从"拼字符串调接口"变成"调本地方法"，类型安全 + 代码可读性飞跃。""",
        "历史,演进,起源,Feign",
    ),
    (
        "OpenFeign 核心原理与架构",
        """## Feign 工作原理

```
UserClient.getUser(1L)
    │
    ├→ JDK 动态代理
    │   Feign.newInstance() 创建代理对象
    │
    ├→ 方法元数据解析
    │   Contract 组件解析 @RequestMapping/@GetMapping 等注解
    │   提取：HTTP 方法、URL 模板、参数位置、Header
    │
    ├→ 构建 RequestTemplate
    │   填充 URL 参数、Body、Header
    │
    ├→ Encoder 编码请求体
    │   默认 JacksonEncoder，把 Java 对象 → JSON
    │
    ├→ Client 发送 HTTP 请求
    │   FeignBlockingLoadBalancerClient 拦截
    │     → LoadBalancer 选择实例
    │     → 替换 URL 中的 service-name 为实际 IP:Port
    │     → 发送 HTTP 请求
    │
    └→ Decoder 解码响应体
        默认 JacksonDecoder，把 JSON → Java 对象
```

## 核心组件

| 组件 | 职责 | 默认实现 |
|------|------|---------|
| **Contract** | 解析注解，提取 HTTP 元数据 | SpringMvcContract |
| **Encoder** | 请求体编码 | JacksonEncoder |
| **Decoder** | 响应体解码 | JacksonDecoder |
| **Client** | 实际发送 HTTP 请求 | Apache HttpClient / OkHttp |
| **Logger** | 日志输出 | Slf4jLogger |
| **Retryer** | 重试策略 | Retryer.NEVER_RETRY（默认不重试）|
| **RequestInterceptor** | 请求拦截器 | 无（可自定义，如注入 Token）|

## Feign 的 JDK 动态代理

```java
// Feign 核心：用 Proxy.newProxyInstance 创建代理
UserClient client = Feign.builder()
    .contract(new SpringMvcContract())    // 解析 Spring MVC 注解
    .encoder(new JacksonEncoder())
    .decoder(new JacksonDecoder())
    .target(UserClient.class, "http://user-service");
```

每次调用 `client.getUser(1L)` 时：
1. `MethodHandler.invoke()` 被触发
2. 构建 HTTP 请求
3. 交给 LoadBalancer 选实例
4. 发送请求，解码响应""",
        "原理,架构,代理,组件",
    ),
    (
        "OpenFeign 进阶配置：超时、重试、拦截器、日志",
        """## 超时配置

```yaml
spring:
  cloud:
    openfeign:
      client:
        config:
          default:
            connectTimeout: 5000      # 连接超时
            readTimeout: 10000        # 读取超时
          user-service:               # 针对特定服务
            connectTimeout: 2000
            readTimeout: 5000
```

## 重试机制

Feign 内置 Retryer，**默认不重试**。需要手动开启：

```java
@Bean
public Retryer feignRetryer() {
    return new Retryer.Default(100, 1000, 3);
    // period=100ms, maxPeriod=1000ms, maxAttempts=3
}
```

> ⚠️ 注意：GET 请求重试通常安全，POST 请求重试一定要保证接口幂等性！

## 请求拦截器（注入 Token）

```java
@Component
public class FeignAuthInterceptor implements RequestInterceptor {
    @Override
    public void apply(RequestTemplate template) {
        // 从 ThreadLocal 或 Spring Security Context 获取 Token
        String token = AuthContextHolder.getToken();
        if (token != null) {
            template.header("Authorization", "Bearer " + token);
        }
    }
}
```

## 日志级别

```yaml
logging:
  level:
    com.example.feign.UserClient: DEBUG  # Feign 接口的日志
```

```java
@Bean
Logger.Level feignLoggerLevel() {
    return Logger.Level.FULL;  // NONE / BASIC / HEADERS / FULL
}
```

| 级别 | 输出内容 |
|------|---------|
| NONE | 不输出（默认）|
| BASIC | 请求方法 + URL + 响应码 + 耗时 |
| HEADERS | BASIC + 请求/响应头 |
| FULL | HEADERS + 请求/响应体 + 元数据 |

## 替换 HTTP Client

Feign 默认用 JDK 的 `HttpURLConnection`（不支持连接池），生产建议换成 Apache HttpClient 或 OkHttp：

```yaml
spring:
  cloud:
    openfeign:
      httpclient:
        enabled: true          # 开启 Apache HttpClient
        max-connections: 200
        max-connections-per-route: 50
```""",
        "超时,重试,拦截器,日志,配置",
    ),
]

FEIGN_INTERVIEWS = [
    (
        "Feign 的原理是什么？它和 RestTemplate 有什么区别？",
        """## Feign 原理

Feign 是一个**声明式 HTTP 客户端**，核心原理是 **JDK 动态代理 + 注解解析**：

1. `@FeignClient` 标注的接口 → Feign 用 `Proxy.newProxyInstance()` 生成代理对象
2. 调用接口方法 → `MethodHandler` 拦截
3. 解析方法上的 Spring MVC 注解（`@GetMapping`、`@RequestParam` 等）→ 构建 `RequestTemplate`
4. Encoder 序列化请求体 → Client 发 HTTP 请求 → Decoder 反序列化响应体

## vs RestTemplate

| 维度 | Feign | RestTemplate |
|------|-------|-------------|
| 编程方式 | 声明式（接口+注解）| 命令式（代码拼接 URL）|
| URL 拼接 | 不用关心 | 手动拼（容易出错）|
| 类型安全 | ✅ 编译期检查 | ❌ 运行时才能发现 |
| 可读性 | 高 | 差 |
| 负载均衡集成 | 与 LoadBalancer 无缝 | 需手动 `@LoadBalanced` |
| 学习成本 | 低（写法 = Spring MVC Controller）| 低 |
| Spring 官方态度 | 推荐（微服务间调用首选）| 标记过时（5.x → WebClient 替代）|

> 面试加分：Spring Boot 3.2 后引入了声明式 `@HttpExchange`（HTTP Interface），是 Feign 的轻量级替代。但 Feign 仍然是微服务间调用最主流的方案。""",
        "原理,RestTemplate,对比,高频",
    ),
    (
        "Feign 调用时如何传递 Token 或链路追踪 ID？如何在 Feign 调用中实现上下文传递？",
        """## 核心答案：通过 RequestInterceptor

```java
@Component
public class FeignAuthInterceptor implements RequestInterceptor {
    @Override
    public void apply(RequestTemplate template) {
        // 从当前请求上下文获取 Token
        ServletRequestAttributes attrs = (ServletRequestAttributes)
            RequestContextHolder.getRequestAttributes();
        if (attrs != null) {
            String token = attrs.getRequest().getHeader("Authorization");
            if (token != null) {
                template.header("Authorization", token);
            }
        }
    }
}
```

## 链路追踪 ID 透传

核心问题：**TraceId 在不同微服务间如何串联？**

Spring Cloud Sleuth / Micrometer Tracing 的做法：
1. `TracingFeignClient` 包装原 Feign Client
2. 每次 Feign 调用前，自动把 `X-B3-TraceId`、`X-B3-SpanId` 写入请求头
3. 下游服务的 Filter 自动读取这些 Header 并恢复 TraceContext

如果不用 Sleuth/Micrometer，自己写透明透传：
```java
@Component
public class TraceInterceptor implements RequestInterceptor {
    @Override
    public void apply(RequestTemplate template) {
        String traceId = MDC.get("traceId");  // 从 MDC 取
        if (traceId != null) {
            template.header("X-Trace-Id", traceId);
        }
    }
}
```

## 线程池上下文的坑

Feign 如果用异步线程调用，`RequestContextHolder` 是 ThreadLocal 绑定的，子线程拿不到父线程的请求属性。解决方案：

```java
// 在主线程调用前手动传递
RequestAttributes attrs = RequestContextHolder.getRequestAttributes();

// 异步线程中手动设置
CompletableFuture.runAsync(() -> {
    RequestContextHolder.setRequestAttributes(attrs);
    userClient.getUser(1L);  // 现在能拿到 Token 了
});
```""",
        "Token,拦截器,透传,链路追踪,上下文",
    ),
]

LB_NOTES = [
    (
        "Spring Cloud LoadBalancer 的历史与原理",
        """## 历史背景

在 Spring Cloud 早期（2015-2019），客户端负载均衡的唯一选择是 **Netflix Ribbon**。然而：

- 2018 年 Netflix 宣布 Ribbon 进入**维护模式**
- Ribbon 的 API 设计不够现代化（ZoneAvoidanceRule、PingUrl 等概念陈旧）
- Ribbon 不支持响应式（WebFlux 无法使用）

2020 年 Spring Cloud Hoxton 发布时，官方推出了 **Spring Cloud LoadBalancer** 作为 Ribbon 的替代品。

## Spring Cloud LoadBalancer 原理

```
@FeignClient(name = "user-service")
    │
    ├→ FeignBlockingLoadBalancerClient
    │   拦截 Feign 的请求，从 service-name 解析为实际 URL
    │
    ├→ DiscoveryClient
    │   从 Nacos/Eureka 获取 "user-service" 的所有可用实例
    │   [192.168.1.10:8080, 192.168.1.11:8080]
    │
    ├→ LoadBalancer（核心）
    │   ServiceInstanceListSupplier 提供实例列表
    │   → ReactorLoadBalancer 选择一个实例
    │   → 返回 http://192.168.1.10:8080
    │
    └→ 发送请求到选中的实例
```

## 两种负载均衡策略

**1. RoundRobinLoadBalancer（默认轮询）**
```java
// 从实例列表中轮询选取
int index = (position + 1) % instances.size();
```

**2. RandomLoadBalancer（随机）**
```java
@Bean
public ReactorLoadBalancer<ServiceInstance> randomLoadBalancer(Environment env,
        LoadBalancerClientFactory factory) {
    String name = env.getProperty("spring.application.name");
    return new RandomLoadBalancer(
        factory.getLazyProvider(name, ServiceInstanceListSupplier.class), name);
}
```

## Ribbon 的 IRule vs LoadBalancer

| Ribbon (旧) | LoadBalancer (新) |
|-------------|------------------|
| RoundRobinRule | RoundRobinLoadBalancer |
| RandomRule | RandomLoadBalancer |
| RetryRule | 内置 RetryableLoadBalancerClient |
| WeightedResponseTimeRule | 需自定义 |
| ZoneAvoidanceRule | 需结合 ServiceInstanceListSupplier 过滤 |

> 迁移口诀：Ribbon 是"先选策略再过滤"，LoadBalancer 是"先过滤再选策略"。LoadBalancer 把实例筛选（健康检查、同机房优先）和选择策略（轮询/随机）解耦了。""",
        "历史,原理,Ribbon,负载均衡,演进",
    ),
]

LB_INTERVIEWS = [
    (
        "Spring Cloud LoadBalancer 和 Ribbon 有什么区别？为什么替换 Ribbon？",
        """## 为什么要替换 Ribbon

1. **Ribbon 进入维护模式**：Netflix 2018 年宣布，不再开发新功能
2. **不支持响应式**：Ribbon 的 API 基于阻塞式 IO，WebFlux 项目无法使用
3. **API 设计过时**：Ribbon 的 `IRule`、`IPing`、`ServerListFilter` 等接口耦合度高
4. **Spring 官方可控**：LoadBalancer 完全由 Spring 团队维护，和 Spring Cloud 生态整合更紧密

## 核心区别

| 维度 | Ribbon | LoadBalancer |
|------|--------|-------------|
| 维护方 | Netflix（停更）| Spring 官方（活跃）|
| 默认策略 | ZoneAvoidanceRule | RoundRobinLoadBalancer |
| 编程模型 | 面向规则（IRule）| 面向选择器（ReactorLoadBalancer）|
| 响应式支持 | ❌ | ✅（Reactor 原生）|
| 配置方式 | 繁琐（Java Config）| 简洁（application.yml）|
| 实例获取 | 独立拉取 | 复用 DiscoveryClient |

## 迁移建议

```yaml
# 只需在配置中去掉 Ribbon 依赖即可
spring:
  cloud:
    loadbalancer:
      ribbon:
        enabled: false  # 显式禁用 Ribbon
```
Spring Cloud 2020.0 版本后 LoadBalancer 已是默认，不需要额外配置。""",
        "Ribbon,对比,替换,原理",
    ),
]

# ====================================================================
# P2: Sentinel + Resilience4j + Circuit Breaker
# ====================================================================

SENTINEL_NOTES = [
    (
        "Sentinel 的历史与定位",
        """## 起源

Sentinel 是由**阿里巴巴中间件团队**开发的流量控制组件，2018 年开源。它的前身是阿里内部的**"哨兵系统"**，用于保护双11流量高峰下的核心链路。

2019 年进入 Spring Cloud Alibaba 生态，替代 Hystrix 成为国内微服务熔断降级的首选。

## 核心概念

| 概念 | 说明 |
|------|------|
| **资源（Resource）** | 需要被保护的代码块，可以是 URL、方法、甚至一段代码 |
| **规则（Rule）** | 对资源的保护策略（流控、熔断、热点...）|
| **流量控制** | 限制通过资源的 QPS/线程数 |
| **熔断降级** | 资源不稳定时自动断开，返回 fallback |
| **热点参数限流** | 对某个参数值（如商品ID）单独限流 |

## 为什么替代 Hystrix

| 维度 | Hystrix | Sentinel |
|------|---------|----------|
| 隔离策略 | 线程池/信号量 | 信号量（轻量）|
| 熔断策略 | 基于错误比例 | 错误比例 + 慢调用比例 + 异常数 |
| 流量控制 | 不支持 | ✅ QPS/线程数/关联/链路 |
| 热点限流 | 不支持 | ✅ 参数级别 |
| 控制台 | Dashboard 功能弱 | ✅ 实时监控 + 规则推送 |
| 规则持久化 | 不支持 | ✅ 支持 Nacos/Apollo/本地文件 |
| 自适应 | ❌ | ✅ 系统自适应限流 |
| 维护状态 | 停更 | 活跃 |

## 流控规则的三种效果

| 效果 | 说明 |
|------|------|
| **快速失败** | 超过阈值直接抛 FlowException（默认）|
| **Warm Up** | 预热，从阈值/3 慢慢升到阈值，防止冷启动压垮DB |
| **排队等待** | 匀速排队，让请求以固定速率通过（漏桶算法）|

> 面试重点：Sentinel 的核心竞争力在于**流量控制 + 熔断降级 + 系统自适应三位一体**，Hystrix 只有熔断。""",
        "历史,定位,Hystrix,对比,流量控制",
    ),
    (
        "Sentinel 的核心原理与滑动窗口",
        """## Sentinel 工作流程

```
请求进入
    │
    ├→ ① 构建调用链（NodeSelectorSlot → ClusterBuilderSlot → ...）
    │
    ├→ ② 遍历所有规则（FlowSlot → DegradeSlot → AuthoritySlot → ...）
    │     └→ 每条规则检查是否触发
    │
    ├→ ③ 触发限流/降级 → 抛出 BlockException
    │     └→ 执行 fallback 逻辑
    │
    └→ ④ 通过所有检查 → 正常执行业务逻辑
          └→ 统计本次调用的 RT、成功/失败等指标
```

## 滑动窗口算法（核心）

Sentinel 统计 QPS 用的不是固定窗口（有突刺问题），而是**滑动窗口**：

```
时间轴 →
窗口长度 = 1s，分成 2 个格子 (每个 500ms)

[  格子A  ]  [  格子B  ]
 t-500ms     t=now

计算 QPS 时：统计格子 A + 格子 B 的请求总数
往下走一个格子：淘汰旧格子，创建新格子
```

默认配置：1 秒窗口分 2 格。精度足够，内存开销小。

## 三种熔断策略

```java
// 慢调用比例
new DegradeRule("resource")
    .setGrade(RuleConstant.DEGRADE_GRADE_RT)
    .setCount(100)       // 最大 RT > 100ms
    .setTimeWindow(10)   // 统计窗口 10s
    .setMinRequestAmount(5)  // 最小请求数
    .setSlowRatioThreshold(0.5);  // 50% 慢调用 → 熔断

// 异常比例
.setGrade(RuleConstant.DEGRADE_GRADE_EXCEPTION_RATIO)
.setCount(0.5);         // 50% 异常率 → 熔断

// 异常数
.setGrade(RuleConstant.DEGRADE_GRADE_EXCEPTION_COUNT)
.setCount(10);          // 1 分钟内 10 个异常 → 熔断
```

熔断状态机：
```
CLOSED（正常）→ 达到阈值 → OPEN（熔断中，快速失败）
                              │
                        过了熔断时长
                              │
                              ↓
                     HALF-OPEN（试探）
                         │
                    ┌────┴────┐
                试探成功    试探失败
                    │         │
                  CLOSED    OPEN
```""",
        "原理,滑动窗口,算法,熔断,降级",
    ),
]

SENTINEL_INTERVIEWS = [
    (
        "Sentinel 的滑动窗口是怎么工作的？和固定窗口有什么不同？",
        """## 固定窗口的问题

固定窗口按秒对齐：比如规定 1 秒最多 100 个请求。

```
时间轴: | 00:00.000 | 00:00.500 | 00:01.000 |
请求:   |    95     |     0     |    95     |
窗口:   [---窗口1: 95个---] [---窗口2: 95个---]

每个窗口都没超 100 → 全部放行
实际 00:00.500~00:01.000 这 0.5s 内涌入了 190 个请求！
```

这就是固定窗口的**"突刺效应"**——窗口边界处流量翻倍。

## 滑动窗口的解法

```
窗口大小 = 1s，格子数 = 4

[g0][g1][g2][g3]
每个格子 = 250ms

计算 QPS = g0+g1+g2+g3 的请求总数
每 250ms 滑动一次：淘汰最旧的 g0，新增 g4
```

Sentinel 默认用 **LeapArray**（环形数组）实现滑动窗口：
- 数组长度 = 窗口大小 / 格子大小
- 每次滑动只更新当前格子的数据
- 计算时遍历所有格子求和

> 面试加分：Sentinel 实际用了**两个滑动窗口**——一个统计每秒 QPS（用于流控），一个统计每分钟异常数（用于熔断）。两个窗口独立滑动。""",
        "滑动窗口,算法,固定窗口,高频",
    ),
    (
        "Sentinel 和 Hystrix 的设计思路有什么本质不同？",
        """## 核心设计差异

**Hystrix 的设计哲学：隔离**
- 每个依赖一个线程池，线程池满就拒绝
- "把有问题的服务关起来，别影响其他服务"
- 优势：隔离性强，一个慢依赖不会拖垮整个系统
- 劣势：线程池开销大，百级依赖 = 百个线程池 = 上千线程

**Sentinel 的设计哲学：控制**
- 不靠线程池隔离，靠 QPS/并发数限制 + 信号量
- "控制流入量，保证系统在安全水位下运行"
- 优势：轻量（无额外线程开销），可以精细控制
- 劣势：隔离性不如 Hystrix 的线程池方案

## 对比表

| 维度 | Hystrix | Sentinel |
|------|---------|----------|
| 核心思路 | 线程池/信号量隔离 | 流量控制（QPS/并发）|
| 熔断维度 | 仅错误比例 | 错误比例/慢调用/异常数 |
| 流量整形 | ❌ | ✅ 匀速排队/Warm Up |
| 自适应 | ❌ | ✅ 系统负载自适应 |
| 规则动态修改 | ❌ 需重启 | ✅ 控制台实时推送 |
| 性能开销 | 较高（线程池）| 较低（滑动窗口内存统计）|
| 维护 | 停更 | 活跃 |

> 面试金句：Hystrix 是"关小黑屋"式的粗暴隔离，Sentinel 是"流量警察"式的精细控制。两者不冲突——大厂实践中 Sentinel 负责限流熔断，资源隔离交给容器/K8s 的配额来控制。""",
        "Hystrix,对比,设计哲学,区别",
    ),
]

RESILIENCE4J_NOTES = [
    (
        "Resilience4j 的历史与设计理念",
        """## 起源

Resilience4j 由 **Robert Winkler** 在 2017 年创建，灵感来自 Hystrix 但采用了完全不同的设计哲学。

Hystrix 对外部依赖的隔离是通过**线程池**实现的——每个下游依赖分配一个独立的线程池。这在 Netflix 的规模下是合理的，但对于大多数项目来说太重了。

Resilience4j 的设计理念是：**不做线程池隔离，只做函数式装饰**。

```java
// Resilience4j 的装饰器模式
Supplier<String> supplier = () -> userService.getUser(id);
Supplier<String> decorated = Decorators.of(supplier)
    .withCircuitBreaker(circuitBreaker)
    .withRetry(retry)
    .withBulkhead(bulkhead)
    .withRateLimiter(rateLimiter)
    .decorate();
String result = decorated.get();
```

## 为什么 Spring Cloud 官方推荐 Resilience4j

| 维度 | Hystrix | Resilience4j |
|------|---------|-------------|
| 隔离策略 | 线程池（重）| 信号量（轻）|
| 函数式 API | ❌ | ✅（装饰器链）|
| 响应式支持 | ❌ | ✅（RxJava/Reactor）|
| 模块按需引入 | ❌（全量）| ✅（按需）|
| 轻量 | ❌ | ✅（核心无外部依赖）|

## 四大核心模块

| 模块 | 作用 | 类比 |
|------|------|------|
| **CircuitBreaker** | 熔断器 | 电闸保险丝 |
| **Retry** | 重试 | 失败重来 |
| **Bulkhead** | 隔离舱（信号量）| 船的分舱 |
| **RateLimiter** | 限流器 | 门口排队 |

> 关键：Resilience4j 在 Spring Cloud Circuit Breaker 抽象层下工作，和 Sentinel 是同一层的不同实现。""",
        "历史,设计理念,装饰器模式,Hystrix",
    ),
    (
        "Resilience4j 熔断器原理：状态机与滑动窗口",
        """## 三状态熔断器

```
CLOSED → OPEN → HALF_OPEN → CLOSED
  │                  │
  │    (正常)        │   (试探)
  └──────────────────┘
```

### CLOSED（关闭 = 正常状态）

所有请求正常通过，同时统计失败率/慢调用率。

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)        // 失败率 50% → 触发熔断
    .slowCallRateThreshold(50)       // 慢调用率 50% → 触发熔断
    .slowCallDurationThreshold(Duration.ofSeconds(2))  // RT > 2s = 慢调用
    .slidingWindowType(SlidingWindowType.COUNT_BASED)  // 基于次数还是时间
    .slidingWindowSize(10)           // 10 次请求为一个窗口
    .minimumNumberOfCalls(5)         // 至少 5 次请求才开始统计
    .build();
```

### OPEN（打开 = 熔断中）

所有请求直接返回 `CallNotPermittedException`，不调用真实服务。保持 `waitDurationInOpenState`（默认 60 秒）。

### HALF_OPEN（半开 = 试探）

过了熔断时间后，允许少量请求通过：
- 请求成功 → 认为服务恢复 → 切回 CLOSED
- 请求失败 → 认为服务未恢复 → 切回 OPEN

## 两种滑动窗口

| 类型 | 原理 | 适用场景 |
|------|------|----------|
| **计数型** | 最近 N 次请求的统计 | 请求量稳定的场景 |
| **时间型** | 最近 N 秒内请求的统计 | 请求量波动大的场景 |

```java
// 计数型：最近 10 次请求中失败 50% → 熔断
.slidingWindowType(SlidingWindowType.COUNT_BASED)
.slidingWindowSize(10)

// 时间型：最近 30 秒的请求中失败 50% → 熔断
.slidingWindowType(SlidingWindowType.TIME_BASED)
.slidingWindowSize(30)
```

## 熔断事件的监听

```java
circuitBreaker.getEventPublisher()
    .onStateTransition(event ->
        log.info("熔断器 {} → {}", event.getStateTransition().getFromState(),
                                      event.getStateTransition().getToState()))
    .onCallNotPermitted(event ->
        log.warn("熔断器拒绝请求"))
    .onError(event ->
        log.error("请求失败, 耗时={}ms", event.getElapsedDuration().toMillis()));
```""",
        "熔断器,状态机,滑动窗口,原理",
    ),
]

RESILIENCE4J_INTERVIEWS = [
    (
        "Resilience4j 的装饰器模式有什么优势？多个装饰器叠加时顺序重要吗？",
        """## 装饰器模式的优势

1. **按需组合**：只用 Retry，就只装饰 Retry，不引入其他模块
2. **函数式**：代码清晰，一行链式调用完成所有保护策略
3. **可测试**：每个组件可独立测试

## 装饰器顺序

顺序**非常重要**，直接影响行为：

```java
// 推荐顺序（外 → 内）
Decorators.of(supplier)
    .withBulkhead(bulkhead)        // 1. 最外层：隔离（限制并发）
    .withRateLimiter(rateLimiter)  // 2. 限流
    .withCircuitBreaker(cb)        // 3. 熔断
    .withRetry(retry)              // 4. 重试（最内层）
    .decorate();
```

为什么这个顺序？
- **Bulkhead 最外层**：先判断是否有空位，没空位直接拒绝，不浪费后续逻辑
- **RateLimiter**：控制整体 QPS
- **CircuitBreaker**：判断服务是否健康
- **Retry 最内层**：只有在"通过熔断检查但调用失败"时才重试

如果把 Retry 放在熔断外面：
```
熔断 OPEN → 请求被拒绝 → Retry → 被拒绝 → Retry → 被拒绝...
                               ↑ 毫无意义的反复重试！
```

> 面试金句：Retry 必须在熔断**里面**。熔断已经判断服务不可用了，外面再重试就是纯浪费资源。""",
        "装饰器,顺序,函数式",
    ),
]

CB_NOTES = [
    (
        "Spring Cloud Circuit Breaker 抽象层",
        """## 为什么需要 Circuit Breaker 抽象

在 Spring Cloud 生态中有多种熔断器实现：Resilience4j、Sentinel、Hystrix（已停更）。如果不做抽象，切换熔断器需要改业务代码。

Spring Cloud Circuit Breaker 提供统一的 API 接口：

```java
// 业务代码只依赖抽象
@Bean
public Customizer<CircuitBreakerFactory<>> defaultCustomizer() {
    return factory -> factory.configureDefault(id ->
        new Resilience4JConfigBuilder(id)
            .circuitBreakerConfig(CircuitBreakerConfig.custom()
                .failureRateThreshold(50)
                .build())
            .build());
}
```

## 支持的实现

| 实现 | 状态 |
|------|------|
| Resilience4j | ✅ Spring 官方推荐 |
| Sentinel | ✅ Spring Cloud Alibaba |
| Hystrix | ❌ 已移除（2021.0 版本后）|

## 使用方式

```java
@RestController
public class OrderController {

    @Autowired
    private CircuitBreakerFactory cbFactory;

    @GetMapping("/order/{id}")
    public Order getOrder(@PathVariable Long id) {
        return cbFactory.create("order-service")
            .run(() -> orderService.getOrder(id),       // 正常逻辑
                 throwable -> getFallbackOrder(id));     // 降级逻辑
    }
}
```

## 注解方式（AOP）

```java
// Sentinel 的 @SentinelResource 或 Resilience4j 的 @CircuitBreaker
@CircuitBreaker(name = "order-service", fallbackMethod = "fallback")
public Order getOrder(Long id) {
    return orderService.getOrder(id);
}

public Order fallback(Long id, Throwable t) {
    return Order.empty();
}
```

> 面试要点：Spring Cloud Circuit Breaker 是一个**统一抽象层**，负责屏蔽不同实现细节。你的代码依赖抽象而非具体实现，换熔断器只要换 starter 依赖 + 改配置即可。""",
        "抽象层,接口,Resilience4j,Sentinel",
    ),
]

CB_INTERVIEWS = [
    (
        "为什么 Spring Cloud 要设计一个 Circuit Breaker 抽象层？",
        """## 核心原因

**解耦业务代码和熔断实现。** 抽象层提供了一个统一的 API，让你可以：

1. 写一次业务代码，随时切换熔断器实现
2. 不用在每个地方 import Resilience4j 或 Sentinel 的具体类
3. 新项目可以用 Sentinel（功能更强），老项目可以用 Resilience4j（轻量）

## 类比

就像 JDBC 之于数据库——你的代码写 JDBC API，底层可以是 MySQL、PostgreSQL、H2。Circuit Breaker 抽象就是熔断界的 JDBC。

## 局限

抽象层只提供最基础的熔断能力，高级功能（如 Sentinel 的流控、热点限流）仍需用各实现的专属 API。""",
        "抽象,设计模式,解耦",
    ),
]

# ====================================================================
# P3: Gateway + Config + Bus
# ====================================================================

GATEWAY_NOTES = [
    (
        "Spring Cloud Gateway 的历史与架构",
        """## 历史背景

2018 年之前，Spring Cloud 的 API 网关是 **Netflix Zuul**。Zuul 基于 Servlet 2.5（阻塞式 IO），不支持 WebSocket、不支持长连接，性能在微服务场景下捉襟见肘。

2018 年 Spring 团队推出了 Spring Cloud Gateway，基于以下新技术栈：
- **Spring WebFlux**（响应式、非阻塞）
- **Project Reactor**（Mono/Flux）
- **Netty**（异步事件驱动网络框架）

## 架构

```
Client Request
     │
     ↓
Netty Server（接收 HTTP 请求）
     │
     ↓
Gateway Handler Mapping（匹配路由）
     │
     ├─ 匹配 Route A？→ 执行 Filter Chain A → 转发到 Service A
     ├─ 匹配 Route B？→ 执行 Filter Chain B → 转发到 Service B
     └─ 无匹配？→ 返回 404
```

## 三大核心概念

| 概念 | 说明 |
|------|------|
| **Route（路由）** | 网关的基本构建块：ID、目标 URI、Predicate、Filter |
| **Predicate（断言）** | 匹配请求条件的规则（如路径匹配、请求头匹配）|
| **Filter（过滤器）** | 对请求/响应做处理的逻辑（如添加请求头、限流）|

## 为什么不用 Zuul

| 维度 | Zuul 1.x | Spring Cloud Gateway |
|------|----------|---------------------|
| IO 模型 | 阻塞（Servlet 2.5）| 非阻塞（Netty）|
| 线程模型 | 一个连接一个线程 | 事件驱动，少量线程 |
| WebSocket | ❌ | ✅ |
| 性能 | 一般 | 优秀（理论上高数倍）|
| 维护 | Netflix 停更 | Spring 官方活跃 |

## 面试重点

Gateway 基于 WebFlux + Netty，所以**不能和传统的 spring-webmvc（Tomcat）共用**。Gateway 是一个独立的应用，MVC 是另一个应用。""",
        "历史,架构,Zuul,WebFlux,Netty",
    ),
    (
        "Gateway 路由、断言、过滤器详解",
        """## 路由配置

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service        # lb = 负载均衡
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=1             # 转发前去掉 /api

        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
            - After=2025-01-01T00:00:00+08:00  # 此时间后生效
          filters:
            - AddRequestHeader=X-Source, gateway
```

## 常用 Predicate（断言）

| 断言 | 示例 | 说明 |
|------|------|------|
| Path | `Path=/api/**` | 路径匹配 |
| Method | `Method=GET,POST` | HTTP 方法 |
| Header | `Header=X-Request-Id,\\d+` | 请求头正则匹配 |
| Query | `Query=token` | Query 参数 |
| Cookie | `Cookie=session,.+` | Cookie 匹配 |
| Host | `Host=**.example.com` | 域名匹配 |
| Before/After/Between | `After=2025-01-01...` | 时间匹配 |
| Weight | `Weight=group1,80` | 权重路由（金丝雀）|

## 常用 Filter

| Filter | 类型 | 说明 |
|--------|------|------|
| StripPrefix | 内置 | 去掉 N 层路径前缀 |
| AddRequestHeader | 内置 | 添加请求头 |
| AddRequestParameter | 内置 | 添加请求参数 |
| PrefixPath | 内置 | 添加路径前缀 |
| RequestRateLimiter | 内置 | 限流（需 Redis）|
| CircuitBreaker | 内置 | 熔断（集成 Resilience4j）|
| Retry | 内置 | 重试 |

## GatewayFilter vs GlobalFilter

- **GatewayFilter**：作用于**特定路由**
- **GlobalFilter**：作用于**所有路由**（如认证、日志）

```java
@Component
public class AuthGlobalFilter implements GlobalFilter, Ordered {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        return chain.filter(exchange);
    }

    @Override
    public int getOrder() { return -100; }
}
```""",
        "路由,断言,过滤器,Predicate,Filter",
    ),
]

GATEWAY_INTERVIEWS = [
    (
        "Spring Cloud Gateway 和 Zuul 有什么区别？为什么选 Gateway？",
        """## 核心区别

| 维度 | Zuul 1.x | Spring Cloud Gateway |
|------|----------|---------------------|
| IO 模型 | 阻塞（BIO）| 非阻塞（NIO）|
| 基于 | Servlet 2.5 | Spring WebFlux + Netty |
| 线程模型 | 一连接一线程 | Event Loop（少量线程）|
| 性能 | 千级并发 | 万级并发 |
| WebSocket | ❌ 不支持 | ✅ 原生支持 |
| 长连接 | ❌ | ✅ |
| 维护状态 | Netflix 停更 + Zuul 2.x 烂尾 | Spring 官方活跃维护 |

## 为什么非阻塞对网关重要

网关是流量入口，所有请求都要经过它。如果网关是阻塞 IO：
- 1000 个并发需要 1000 个线程
- 下游服务慢 → 线程全部阻塞 → 新请求进不来 → 网关成为瓶颈

Gateway 用 Netty 的 Event Loop：
- 少量线程（通常 = CPU 核数 × 2）
- IO 操作异步执行，不阻塞线程
- 下游服务慢不会耗尽网关线程

## Zuul 2.x 呢

Netflix 做了 Zuul 2.x（基于 Netty），但社区采用率极低。Spring 团队选择自己写 Gateway，因为：
1. WebFlux 生态更完善
2. 和 Spring Cloud 其他组件整合更方便
3. 不受 Netflix 开源策略影响

> 面试金句：网关选型看 IO 模型。阻塞网关（Zuul 1.x）是传统 Servlet 容器时代的产物，非阻塞网关（Gateway）才是云原生时代的选择。""",
        "Zuul,对比,非阻塞,性能,高频",
    ),
    (
        "Gateway 的限流是怎么实现的？用什么算法？",
        """## 实现方式：RequestRateLimiter

Gateway 内置了限流 Filter，基于 **Redis + 令牌桶算法**。

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: rate-limit-route
          uri: lb://user-service
          predicates:
            - Path=/api/**
          filters:
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10   # 每秒新增 10 个令牌
                redis-rate-limiter.burstCapacity: 20    # 令牌桶容量 20
                key-resolver: "#{@userKeyResolver}"     # 按什么粒度限流
```

## KeyResolver：决定限流粒度

```java
// 按 IP 限流
@Bean
public KeyResolver ipKeyResolver() {
    return exchange -> Mono.just(
        exchange.getRequest().getRemoteAddress().getAddress().getHostAddress());
}

// 按用户限流
@Bean
public KeyResolver userKeyResolver() {
    return exchange -> Mono.just(
        exchange.getRequest().getQueryParams().getFirst("userId"));
}

// 按接口限流
@Bean
public KeyResolver apiKeyResolver() {
    return exchange -> Mono.just(
        exchange.getRequest().getPath().value());
}
```

## Redis 中存储的内容

```
Key: request_rate_limiter.{key}.tokens
Key: request_rate_limiter.{key}.timestamp

每次请求 → 执行 Lua 脚本（原子操作）
  → 计算当前令牌数
  → 令牌够 → 扣令牌 + 放行
  → 令牌不够 → 返回 429 Too Many Requests
```

> 面试加分：Gateway 的限流是**单机限流逻辑 + Redis 全局计数**，网关层水平扩展时 Redis 保证限流准确。""",
        "限流,令牌桶,Redis,RequestRateLimiter",
    ),
]

CONFIG_NOTES = [
    (
        "Spring Cloud Config 的历史与原理",
        """## 历史背景

在 Config 出现之前，配置管理是微服务的一个痛点：
1. 每个服务有自己的 `application.yml`，打包在 jar 里
2. 改配置 → 重新打包 → 重新部署，"改一个超时参数要发版"
3. 多环境管理靠 profile 命名约定，容易搞混

Spring Cloud Config 2016 年发布，拉开了"配置外部化"的序幕。

## 工作原理

```
┌──────────┐   ┌────────────┐   ┌───────────┐
│  Config   │   │   Git /    │   │           │
│  Server   │←──│   SVN /    │   │  RabbitMQ │
│           │   │  Native FS │   │  (Bus)    │
└─────┬─────┘   └────────────┘   └─────┬─────┘
      │ ①拉取配置                       │
      ↓                                │
┌──────────┐                          │
│  Config   │  ②配置变更 → 发消息到 Bus─┘
│  Client   │
│(order-svc)│
└──────────┘
```

**Config Server**：
- 连接到 Git 仓库（或 SVN / 本地文件系统）
- 提供 REST API：`/{application}/{profile}`
  例如：`GET /order-service/dev` → 返回 order-service-dev.yml 的内容

**Config Client**：
- 启动时调用 Config Server 拉取配置
- 配置通过 `@RefreshScope` 动态刷新

## 配置文件的匹配规则

```
请求: /order-service/dev/main

Config Server 按顺序尝试:
1. order-service-dev.yml
2. order-service.yml
3. application-dev.yml  (共享配置)
4. application.yml      (全局共享配置)
```

这让你可以做到：公共配置放 `application.yml`，服务独有配置放 `{service-name}.yml`。

## 为什么不直接用 Nacos Config

| 维度 | Config + Git | Nacos Config |
|------|-------------|-------------|
| 配置存储 | Git 仓库 | MySQL（Nacos 内置）|
| 配置格式 | 仅 YAML/Properties | YAML/Properties/JSON/XML |
| 版本追溯 | Git 天然支持 | Nacos 内置历史版本 |
| Web 界面 | ❌ 需额外 | ✅ 控制台编辑 |
| 权限控制 | Git 仓库权限 | Nacos RBAC |
| 灰度发布 | ❌ 无 | ✅ 标签灰度 |
| 运维复杂度 | 需维护 Git + Server 集群 | 同 Nacos 集群 |

> 趋势：国内新项目直接用 Nacos Config，免运维 Git 仓库。Config 对已有 Git 基础设施的团队仍有价值。""",
        "历史,原理,配置外部化,Git,Config",
    ),
]

CONFIG_INTERVIEWS = [
    (
        "Spring Cloud Config 配置刷新需要重启吗？如何做到不重启？",
        """## 答案：不需要重启

Spring Cloud Config 配合以下组件实现不重启刷新配置：

### 1. @RefreshScope

```java
@RefreshScope  // ← 这个 Bean 可以动态刷新
@RestController
public class OrderController {
    @Value("${order.timeout}")
    private int timeout;
}
```

刷新步骤：
```
① 修改 Git 上的配置文件
② POST /actuator/refresh → 触发 RefreshEvent
③ ContextRefresher 销毁 @RefreshScope 标注的 Bean
④ 下次请求 → 重新创建 Bean → 读取新配置
```

### 2. Spring Cloud Bus（批量刷新）

一个服务刷新了，如果手动调每个服务的 `/actuator/refresh` 太烦。因为用 Bus：

```
Config Server (通知发起者)
    │ POST /actuator/busrefresh
    │
    └→ RabbitMQ / Kafka
          │
          ├→ order-service  收到 RefreshRemoteApplicationEvent → 自动 refresh
          ├→ user-service   收到 RefreshRemoteApplicationEvent → 自动 refresh
          └→ pay-service    收到 RefreshRemoteApplicationEvent → 自动 refresh
```

一个 POST 请求，所有服务自动刷新。

### 3. 局限性

@RefreshScope 不是万能的：
- 只会重建**被标注的 Bean**，其他 Bean 不受影响
- 数据库连接等资源不会自动重建（需要在 @PreDestroy 释放 + @PostConstruct 重连）
- @RefreshScope 的 Bean 不再是单例，每次刷新建新的""",
        "刷新,@RefreshScope,动态配置",
    ),
]

BUS_NOTES = [
    (
        "Spring Cloud Bus 的历史与原理",
        """## 历史背景

Spring Cloud Bus 2016 年发布，定位是：**连接微服务节点和轻量级消息代理**。

没有 Bus 时，想通知所有节点刷新配置，需要手动调 N 个节点的 `/actuator/refresh`。有了 Bus，一个节点收到通知 → 广播到 MQ → 全部节点自动刷新。

## 工作原理

```
Config Server
    │ POST /actuator/busrefresh
    │
    ↓ 发送 RefreshRemoteApplicationEvent
RabbitMQ / Kafka
    │
    ├→ Node 1 (order-service)   收到事件 → refresh
    ├→ Node 2 (order-service)   收到事件 → refresh
    ├→ Node 3 (user-service)    收到事件 → refresh
    └→ Node 4 (user-service)    收到事件 → refresh
```

## 核心依赖

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-bus-amqp</artifactId>  <!-- RabbitMQ -->
</dependency>
<!-- 或 -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-bus-kafka</artifactId>  <!-- Kafka -->
</dependency>
```

## Bus 事件类型

| 事件 | 作用 |
|------|------|
| `RefreshRemoteApplicationEvent` | 通知刷新配置 |
| `EnvironmentChangeRemoteApplicationEvent` | 通知环境变量变更 |

## 自定义 Bus 事件

```java
// 1. 定义事件
public class CustomEvent extends RemoteApplicationEvent {
    private String message;
}

// 2. 发布事件
@Autowired
private ApplicationContext context;
context.publishEvent(new CustomEvent(this, "my-message"));

// 3. 监听事件
@EventListener
public void handleCustomEvent(CustomEvent event) {
    log.info("收到自定义事件: {}", event.getMessage());
}
```

> 面试要点：Bus 的本质是"基于 MQ 的微服务事件广播"。只要一个节点发出了事件，MQ 会保证所有节点都收到。""",
        "历史,原理,Message Broker,事件广播",
    ),
]

BUS_INTERVIEWS = [
    (
        "Spring Cloud Bus 和 RabbitMQ 是什么关系？Bus 能不用 MQ 吗？",
        """## 关系

Bus 是**消息总线的抽象层**，RabbitMQ 只是它的一个**传输实现**。

```
Spring Cloud Bus（抽象）
    ├── RabbitMQ 实现 (spring-cloud-starter-bus-amqp)
    ├── Kafka 实现 (spring-cloud-starter-bus-kafka)
    └── ... 也可以有其他 MQ 实现
```

Bus 做的事情：封装 MQ 连接的细节，提供统一的事件发布/订阅接口。RabbitMQ/Kafka 是底层传输管道。

## 能不用 MQ 吗

理论上可以，但实践中 Bus 的设计就是依赖 MQ 的。因为它的核心价值是**去中心化的广播**——任意节点发消息，所有节点收到。不用 MQ 就失去广播能力了。

如果你不需要广播（比如只有一个 Config Client 实例），直接调 `/actuator/refresh` 就够了，完全不需要 Bus。""",
        "MQ,RabbitMQ,关系,消息总线",
    ),
]

# ====================================================================
# P4: Stream + SkyWalking + Micrometer
# ====================================================================

STREAM_NOTES = [
    (
        "Spring Cloud Stream 的历史与设计哲学",
        """## 起源

2016 年发布，目标：**让开发者用统一的编程模型操作不同的消息中间件**。

在没有 Stream 之前：
- 用 RabbitMQ → 学 RabbitMQ API
- 用 Kafka → 学 Kafka API
- 切中间件 → 重写所有消息相关代码

有了 Stream 之后：
```java
// 同一套代码，切换 binder 就能换中间件
@Bean
public Function<String, String> process() {
    return input -> "processed: " + input;
}
```

## 核心概念

| 概念 | 说明 |
|------|------|
| **Binder** | 绑定器，适配具体 MQ（RabbitMQ Binder、Kafka Binder）|
| **Binding** | 绑定，连接应用和 MQ 的通道 |
| **Channel** | 通道，消息传输的抽象（input/output）|
| **Destination** | 目的地，MQ 中的 topic/queue |

```
Application
    │
    ├── INPUT Binding  ← 从 MQ 消费消息
    │
    └── OUTPUT Binding  → 向 MQ 发送消息
```

## 函数式编程（3.x+）

```java
// 旧写法（注解式，已废弃）
@StreamListener(Sink.INPUT)
public void handle(String msg) { ... }

// 新写法（函数式，推荐）
@Bean
public Consumer<String> consume() {
    return msg -> log.info("收到: {}", msg);
}

@Bean
public Supplier<String> produce() {
    return () -> "hello";
}

@Bean
public Function<String, String> process() {
    return input -> input.toUpperCase();  // 有输入有输出
}
```

配置：
```yaml
spring:
  cloud:
    function:
      definition: consume;produce;process  # 注册函数
    stream:
      bindings:
        consume-in-0:
          destination: my-topic
        produce-out-0:
          destination: my-topic
        process-in-0:
          destination: input-topic
        process-out-0:
          destination: output-topic
```

> 命名规则：`<functionName>-<in|out>-<index>`。in=输入，out=输出。""",
        "历史,设计哲学,Binder,函数式",
    ),
]

STREAM_INTERVIEWS = [
    (
        "Spring Cloud Stream 如何屏蔽不同 MQ 的差异？为什么要用 Binder？",
        """## Binder 机制

Binder 是 Stream 的核心抽象，它屏蔽了不同 MQ 的 API 差异：

```
你的代码
    ↓ 调用 Stream API
Spring Cloud Stream 核心
    ↓ 调用 Binder SPI
RabbitMQ Binder / Kafka Binder
    ↓ 翻译为原生 API
RabbitMQ SDK / Kafka SDK
```

## Binder 负责什么

| 职责 | RabbitMQ 实现 | Kafka 实现 |
|------|-------------|-----------|
| 创建 Queue/Topic | 自动创建 Exchange + Queue | 自动创建 Topic |
| 绑定关系 | Binding → Exchange 路由 | Binding → Partition 分配 |
| 消费组 | Queue 同名 → 共享消费 | Consumer Group |
| 分区 | ❌ 不支持 | ✅ Kafka Partition |

## 切换 MQ 只需改依赖

```xml
<!-- RabbitMQ -->
<dependency>
    <artifactId>spring-cloud-stream-binder-rabbit</artifactId>
</dependency>

<!-- 切换到 Kafka：只改这一个依赖！-->
<dependency>
    <artifactId>spring-cloud-stream-binder-kafka</artifactId>
</dependency>
```

> 面试金句：Binder 的设计是适配器模式在消息领域的经典应用。你写的是 Stream 通用 API，Binder 帮你翻译成具体 MQ 的方言。""",
        "Binder,适配器,抽象,MQ",
    ),
]

SKYWALKING_NOTES = [
    (
        "SkyWalking 的历史与架构",
        """## 起源

SkyWalking 由**吴晟**（Sheng Wu）在 2015 年创建，最初是个人项目，后来进入 Apache 基金会成为顶级项目。是国内最主流、全球也广泛使用的 APM 系统之一。

## 解决的问题

在微服务架构中，一个请求可能经过 N 个服务。当出现慢请求时：
- 是哪个服务慢？
- 是数据库慢还是 RPC 慢？
- 整条链路的拓扑是怎样的？

SkyWalking 通过**自动探针**无侵入地回答这些问题。

## 架构

```
┌─────────────────────────────┐
│     SkyWalking UI           │  可视化面板
│   (拓扑图/追踪/告警/指标)     │
└─────────────┬───────────────┘
              │ gRPC/HTTP
┌─────────────┴───────────────┐
│     SkyWalking OAP Server   │  核心分析引擎
│   (接收数据 → 分析 → 聚合)    │
└─────────────┬───────────────┘
              │ gRPC (定期上报)
    ┌─────────┼─────────┐
    │         │         │
┌───┴──┐ ┌───┴──┐ ┌───┴──┐
│Agent │ │Agent │ │Agent │      Java Agent（字节码增强）
│Svc A │ │Svc B │ │Svc C │
└──────┘ └──────┘ └──────┘
```

## Java Agent 零侵入

SkyWalking 通过 `-javaagent` 启动参数注入探针，**不需要改一行业务代码**：

```bash
java -javaagent:/path/to/skywalking-agent.jar \
     -DSW_AGENT_NAME=order-service \
     -DSW_AGENT_COLLECTOR_BACKEND_SERVICES=oap-server:11800 \
     -jar app.jar
```

Agent 在类加载时通过**字节码增强（ByteBuddy）**自动在关键方法前后插入探针代码。

## 和 Sleuth 的区别

| 维度 | Sleuth | SkyWalking |
|------|--------|-----------|
| 侵入性 | 需添加依赖 | 零侵入（javaagent）|
| 数据上报 | HTTP → Zipkin | gRPC → OAP Server |
| 可视化 | 依赖 Zipkin UI | 自带 UI，功能更丰富 |
| 性能影响 | 低 | 低（字节码增强，几乎无开销）|
| 告警 | ❌ | ✅ 内置 |
| 生态 | Spring 官方（已归档迁移到 Micrometer Tracing）| Apache 顶级项目 |""",
        "历史,架构,APM,Java Agent,字节码增强",
    ),
]

SKYWALKING_INTERVIEWS = [
    (
        "SkyWalking 的探针原理是什么？为什么能做到零侵入？",
        """## Java Agent 机制

SkyWalking 利用了 JVM 的 `premain` 机制（Java Agent）：

```
启动时: java -javaagent:skywalking-agent.jar -jar app.jar
                    │
                    ↓
        JVM 调用 premain() (在 main() 之前)
                    │
                    ↓
        SkyWalking Agent 初始化
          ├── 注册 ByteBuddy Transformer
          ├── 加载插件（Spring MVC, MySQL, Feign, Kafka...）
          └── 匹配需要增强的类
                    │
                    ↓
        类加载时
          ├── 匹配到 Spring MVC Controller？
          │     → 在方法前后插入 Trace 代码
          ├── 匹配到 JDBC PreparedStatement？
          │     → 在 execute 前后插入 DB 耗时统计
          └── 匹配到 Feign Client？
                → 在调用前后插入 TraceId 透传代码
```

## ByteBuddy 做了什么

```java
// 原始代码
@GetMapping("/user/{id}")
public User getUser(@PathVariable Long id) {
    return userService.findById(id);
}

// SkyWalking Agent 在加载时自动增强为：
@GetMapping("/user/{id}")
public User getUser(@PathVariable Long id) {
    Span span = ContextManager.createEntrySpan("/user/{id}", ...);
    try {
        User result = userService.findById(id);  // 原始逻辑
        span.setStatus(Status.OK);
        return result;
    } catch (Exception e) {
        span.log(e);
        span.setStatus(Status.ERROR);
        throw e;
    } finally {
        ContextManager.stopSpan();
    }
}
```

这一切在类加载时自动完成，源码完全不动。

> 面试金句：SkyWalking 的"零侵入"不是不做事，而是把事做在了你看不到的地方——JVM 类加载阶段。""",
        "探针,Java Agent,字节码增强,ByteBuddy,高频",
    ),
]

MICROMETER_NOTES = [
    (
        "Micrometer Tracing 的历史与定位",
        """## 起源

Micrometer 最初是一个指标（Metrics）门面库，2018 年成为 Spring Boot 2.x 的默认指标框架。类比 SLF4J 之于日志，Micrometer 就是指标界的 SLF4J——你写一套代码，导出到 Prometheus / Datadog / InfluxDB 任意平台。

2022 年，Spring 团队将 Sleuth 的链路追踪能力也合并到 Micrometer，形成了 **Micrometer Tracing**。Sleuth 项目正式归档。

## 定位

```
应用代码
    │
    ├── Metrics（指标）→ Micrometer → Prometheus / Datadog / ...
    │   例：http.server.requests.count, jvm.memory.used
    │
    └── Tracing（追踪）→ Micrometer Tracing → Brave / OpenTelemetry
        例：TraceId=abc, SpanId=123
```

## Sleuth → Micrometer Tracing 迁移

| Sleuth 概念 | Micrometer Tracing 概念 |
|-------------|----------------------|
| TraceId | traceId（不变）|
| SpanId | spanId（不变）|
| Brave 自动配置 | `micrometer-tracing-bridge-brave` |
| `Tracer` Bean | `ObservationRegistry` + `Observation` |

## 为什么值得关注

1. **统一 API**：指标和追踪不再用两套 API
2. **Observability**：Spring Boot 3.x 的核心概念，Actuator + Micrometer + Tracing 三位一体
3. **未来方向**：Spring 官方已经把宝押在 Micrometer 上，Sleuth 不会再更新""",
        "历史,定位,Sleuth,指标,追踪,统一",
    ),
]

MICROMETER_INTERVIEWS = [
    (
        "Micrometer Tracing 和 Sleuth 的关系？为什么 Sleuth 被淘汰了？",
        """## 关系

Sleuth 是过去（已归档），Micrometer Tracing 是未来。

Spring 团队的决定：与其维护两个分开的库（Micrometer 做指标 + Sleuth 做追踪），不如把追踪能力合并到 Micrometer，统一为"观测性三件套"：Logging + Metrics + Tracing。

## Sleuth 被淘汰的原因

1. **功能重叠**：Sleuth 和 Micrometer 都做观测，但 API 风格不同，开发者要学两套
2. **OpenTelemetry 标准兴起**：行业在向 OTel 收敛，Micrometer Tracing 天然支持 OTel 协议
3. **维护成本**：维护两个库的成本 > 合并为一个
4. **Spring Boot 3.x 重构窗口**：3.x 是大版本，正好做架构性调整

## 迁移建议

新项目直接上 Micrometer Tracing + Brave 或 Micrometer Tracing + OpenTelemetry。老项目如果还在用 Sleuth，除非升级 Spring Boot 3.x，否则没必要强行迁移。""",
        "Sleuth,关系,迁移,OpenTelemetry",
    ),
]

# ====================================================================
# P5: Seata + MyBatis-Plus + K8s + Admin + Task + Contract
# ====================================================================

SEATA_NOTES = [
    (
        "Seata 的历史与分布式事务问题",
        """## 分布式事务的由来

在单体应用中，事务很简单：
```java
@Transactional
public void createOrder() {
    orderDao.insert(order);     // 操作本地 DB
    inventoryDao.deduct(itemId); // 操作本地 DB
}
// 要么全成功，要么全回滚
```

在微服务架构中，同一个业务操作涉及多个服务各自的数据库：
```
Order Service (DB-A) → Inventory Service (DB-B) → Payment Service (DB-C)
```
这三个数据库的写操作怎么保证一致性？

## Seata 的诞生

Seata（Simple Extensible Autonomous Transaction Architecture）由**阿里巴巴**在 2019 年开源，前身是阿里内部的分布式事务中间件 **TXC**（后改名 Fescar，再改名 Seata）。

## Seata 四种模式

| 模式 | 原理 | 一致性 | 性能 | 适用场景 |
|------|------|--------|------|----------|
| **AT** | 自动反向补偿（UNDO_LOG 回滚）| 最终一致性 | 高 | 最常用，业务无侵入 |
| **TCC** | 手动 Try-Confirm-Cancel | 最终一致性 | 很高 | 对一致性要求极高 |
| **Saga** | 正向补偿（一个失败则执行各阶段反向操作）| 最终一致性 | 最高 | 长事务/多步骤 |
| **XA** | 两阶段提交（2PC）| 强一致性 | 低 | 少量对强一致性有要求的场景 |

## AT 模式原理（最常用）

```
① 一阶段：执行业务 SQL + 记录 UNDO_LOG（在同一个本地事务中）
② 二阶段：
   - 全部成功 → 异步删除 UNDO_LOG
   - 有失败 → 根据 UNDO_LOG 自动生成反向 SQL 回滚
```

关键：UNDO_LOG 记录了修改前的数据快照。如果回滚，用快照生成反向 UPDATE/DELETE/INSERT。""",
        "历史,分布式事务,AT,TCC,Saga,XA",
    ),
    (
        "Seata AT 模式原理深度解析",
        """## AT 模式的两阶段提交（改良版 2PC）

```
全局事务开始 (xid = uuid)
    │
    ├→ 分支事务 1: Order Service
    │     INSERT INTO orders ...         ← 业务 SQL
    │     INSERT INTO undo_log ...       ← 自动记录回滚日志
    │     提交本地事务
    │
    ├→ 分支事务 2: Inventory Service
    │     UPDATE inventory SET count=count-1 WHERE id=123
    │     INSERT INTO undo_log ...       ← 记录 count 修改前的值
    │     提交本地事务
    │
    └→ TC（事务协调器）判断：
         ├── 全成功 → 通知所有 RM 异步删除 UNDO_LOG
         └── 有失败 → 通知 RM 根据 UNDO_LOG 回滚
```

## UNDO_LOG 里存什么

```json
{
  "beforeImage": { "rows": [{"id": 123, "count": 10}] },  // 修改前
  "afterImage":  { "rows": [{"id": 123, "count": 9}]  },  // 修改后
  "sqlType": "UPDATE"
}
```

回滚时：读取 beforeImage，生成反向 SQL：`UPDATE inventory SET count=10 WHERE id=123`

## 关键特性

- **一阶段即提交**：不持有锁，本地事务直接提交
- **读已提交隔离**：一阶段提交后，修改对其他事务可见
- **全局锁**：在二阶段完成前，被修改的行会被 Seata 全局锁保护，防止脏写

## 和 XA 模式的关键区别

| 维度 | XA (传统 2PC) | AT (Seata 改良 2PC) |
|------|-------------|-------------------|
| 一阶段 | 预提交，持有数据库锁 | 直接提交，释放数据库锁 |
| 锁持有时间 | 长（从一阶段到二阶段）| 短（仅全局锁，非数据库锁）|
| 并发性能 | 低 | 高 |
| 回滚方式 | 数据库 XA 接口回滚 | 反向 SQL 回滚 |
| 数据库支持 | 需要支持 XA 协议 | 支持 ACID 即可 |""",
        "AT模式,UNDO_LOG,原理,两阶段,回滚",
    ),
]

SEATA_INTERVIEWS = [
    (
        "Seata 的 AT 模式和 TCC 模式有什么区别？各自适用什么场景？",
        """## 核心区别

| 维度 | AT | TCC |
|------|-----|-----|
| 侵入性 | 无侵入（自动记录 UNDO_LOG）| 高侵入（手动写 Try/Confirm/Cancel）|
| 实现复杂度 | 低（加注解即可）| 高（三个接口都要写）|
| 性能 | 高（自动补偿）| 很高（无锁）|
| 回滚方式 | 自动反向 SQL | 手动 Cancel 逻辑 |
| 适用场景 | 大部分分布式事务场景 | 对一致性/性能要求极高的核心链路 |

## TCC 示例

```java
// Try: 预留资源
public void tryDeduct(String userId, BigDecimal amount) {
    // 冻结余额
    accountService.freeze(userId, amount);  // available → frozen
}

// Confirm: 确认使用
public void confirmDeduct(String userId, BigDecimal amount) {
    // 真正扣减
    accountService.unfreezeAndDeduct(userId, amount);  // frozen → deducted
}

// Cancel: 释放资源
public void cancelDeduct(String userId, BigDecimal amount) {
    // 解冻
    accountService.unfreeze(userId, amount);  // frozen → available
}
```

## 选型建议

> AT 模式能用 AT 就用 AT（开发成本低）。TCC 只在极端重视性能且团队成员对 TCC 模式足够熟悉时才用——写 Cancel 逻辑比看上去难得多，边界情况极多。""",
        "AT,TCC,对比,选型,高频",
    ),
    (
        "分布式事务有哪些常见方案？Seata 的优势在哪里？",
        """## 常见方案对比

| 方案 | 类型 | 一致性 | 性能 | 实现复杂度 |
|------|------|--------|------|-----------|
| **Seata AT** | 自动补偿 | 最终 | 高 | 低 |
| **Seata TCC** | 手动补偿 | 最终 | 很高 | 高 |
| **RocketMQ 事务消息** | 消息驱动 | 最终 | 高 | 中 |
| **本地消息表** | 消息驱动 | 最终 | 中 | 中 |
| **Saga** | 编排补偿 | 最终 | 最高 | 高 |
| **XA/2PC** | 强一致性 | 强 | 低 | 低（但数据库要支持）|

## Seata 的优势

1. **AT 模式几乎零侵入**：加 `@GlobalTransactional` 即可
2. **支持多种模式**：AT、TCC、Saga、XA 根据场景灵活选
3. **阿里背书**：双11 级别的流量验证
4. **生态融合**：Spring Cloud Alibaba 原生支持

## 何时不用 Seata

- 业务量很小（2-3 个服务）→ 本地消息表足够
- 可以接受最终一致性但不接受全局锁 → Saga
- 强一致性要求 + 数据库支持 XA → 直接用 XA 模式""",
        "方案对比,选型,优势",
    ),
]

MYBATIS_NOTES = [
    (
        "MyBatis-Plus 的历史与定位",
        """## 起源

MyBatis-Plus 由**青苗**（baomidou）在 2016 年创建，最初是个人对 MyBatis 的增强工具包。核心思想：**只做增强不做改变**——你以前怎么写 MyBatis，现在还是一样写，只是多了很多省力的方法。

MyBatis 最大的痛点：写单表 CRUD 太无聊了。一张表 → Mapper.xml → `<resultMap>` → `<insert>` → `<select>` → `<update>` → `<delete>` ——重复劳动。

MyBatis-Plus 的解法：**继承 BaseMapper，单表 CRUD 自动拥有**。

## 核心能力

```java
public interface UserMapper extends BaseMapper<User> {
    // 不用写任何方法，自带了：
    // insert, deleteById, deleteBatchIds, updateById, update,
    // selectById, selectBatchIds, selectList, selectPage, selectCount...
}
```

## 为什么 Spring Boot 项目标配它

| 对比 | 手写 MyBatis | MyBatis-Plus |
|------|-------------|-------------|
| 单表 CRUD | 每表写一遍 Mapper.xml | 继承 BaseMapper 即用 |
| 分页 | 手写 limit offset + count | `Page<User> page = new Page<>(1,10);` |
| 条件查询 | 手写 `<if>` 判断 | Lambda 链式：`eq(User::getName,"张三")` |
| 主键生成 | 手写 `selectKey` | `@TableId(type = IdType.ASSIGN_ID)` 雪花 |
| 逻辑删除 | 手改 SQL | `@TableLogic` 自动改 WHERE deleted=0 |
| 乐观锁 | 手写 version 判断 | `@Version` 自动注入 version+1 |

> MyBatis-Plus 的哲学：CRUD 是机器应该做的事，开发者的时间应该花在复杂的多表关联查询上。""",
        "历史,定位,MyBatis,BaseMapper,增强",
    ),
]

MYBATIS_INTERVIEWS = [
    (
        "MyBatis-Plus 的分页是怎么实现的？和 MyBatis 分页插件冲突怎么办？",
        """## MyBatis-Plus 分页原理

MyBatis-Plus 的分页通过 **MyBatis 插件机制（Interceptor）** 实现：

```java
// 配置分页插件
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
    return interceptor;
}

// 使用
Page<User> page = new Page<>(1, 10);  // 第 1 页，10 条
IPage<User> result = userMapper.selectPage(page, null);
```

底层原理：
```
拦截 Executor.query()
    → 执行 COUNT 查询（获取总记录数）
    → 修改原始 SQL：添加 LIMIT ?,?
    → 执行分页查询
    → 返回 Page 对象（含 records, total, pages, current）
```

## 和 PageHelper 冲突

PageHelper 和 MyBatis-Plus 都是通过 MyBatis Interceptor 实现分页的。如果两个插件同时存在，**都会拦截 SQL 并添加 LIMIT 子句**——结果就是 SQL 里有两条 `LIMIT` 语句，直接报错。

解决方案：二选一。用了 MyBatis-Plus 就不要用 PageHelper。""",
        "分页,插件,PageHelper,原理",
    ),
]

K8S_NOTES = [
    (
        "Spring Cloud Kubernetes 的历史与原理",
        """## 为什么要 Spring Cloud on K8s

传统的 Spring Cloud 依赖 Eureka/Nacos 做服务发现，依赖 Config 做配置管理。但 K8s 本身就提供了 Service（服务发现）和 ConfigMap/Secret（配置管理）。

这就产生了一个问题：**在 K8s 上跑 Spring Cloud 时，是用 K8s 原生的能力，还是用 Spring Cloud 的一套？**

Spring Cloud Kubernetes 的目标：**让你在 K8s 上享受原生的服务发现和配置，同时保持 Spring Cloud 的编程模式**。

## 核心功能

```yaml
# 开启 K8s 原生服务发现
spring:
  cloud:
    kubernetes:
      discovery:
        enabled: true
```

效果：`@FeignClient(name = "user-service")` 中的 `user-service` 不再查 Nacos/Eureka，而是查 K8s Service。

## K8s Service → Spring Cloud 服务发现的映射

| K8s 概念 | Spring Cloud 概念 |
|----------|------------------|
| Service | 服务名 |
| Pod | 实例 |
| Service Port | 端口 |
| Namespace | 隔离域 |
| ConfigMap | 配置来源 |
| Secret | 加密配置 |

> 面试要点：如果你的服务最终部署在 K8s 上，用 Spring Cloud Kubernetes 可以减少一层中间件依赖（不部署 Nacos/Eureka），架构更简洁。""",
        "K8s,Kubernetes,服务发现,配置,云原生",
    ),
]

K8S_INTERVIEWS = [
    (
        "在 K8s 上部署 Spring Cloud 还需要 Nacos/Eureka 吗？",
        """## 答案：不一定

K8s 原生已经提供了服务发现（Service + DNS）和配置管理（ConfigMap + Secret）。

### 可以不用的场景

- 全部服务都在同一个 K8s 集群内
- 不需要灰度发布、权重路由等高级特性
- 能接受 K8s Service 的轮询负载均衡

用 `spring-cloud-starter-kubernetes-discovery`，Feign 调用直接用 K8s Service 名。

### 仍需要的场景

- **跨集群调用**：K8s Service 只管本集群，多集群间需要 Nacos
- **灰度发布/金丝雀流量**：Nacos 的权重路由比 K8s Service 灵活
- **团队习惯**：开发排错时，Nacos 控制台比 `kubectl describe svc` 友好太多
- **非 K8s 环境**：开发/测试可能不用 K8s，这时 Nacos 仍然需要

> 实践：大多数团队选择**保留 Nacos**，因为 Nacos 的功能 >> K8s Service，而且运维成本差异不大。""",
        "K8s,服务发现,Nacos,对比",
    ),
]

ADMIN_NOTES = [
    (
        "Spring Boot Admin 的历史与原理",
        """## 起源

Spring Boot Admin（SBA）由 **Johannes Edmeier** 在 2015 年创建，是一个开源社区项目（非 Spring 官方），用于监控和管理 Spring Boot 应用。

## 架构

```
┌──────────────────┐
│  Admin Server    │  ← 一个独立应用，可视化面板
│  (端口 9090)     │
└────────┬─────────┘
         │ 通过 Actuator 端点拉取数据
    ┌────┼────┐
    │    │    │
┌───┴─┐┌─┴───┐┌┴───┐
│ App ││ App ││ App │  ← 被监控的 Spring Boot 应用
│  A  ││  B  ││  C  │     (需引入 spring-boot-actuator)
└─────┘└─────┘└─────┘
```

## 核心功能

- 查看所有应用的健康状态、版本、JVM 信息
- 在线修改日志级别（不用重启）
- 查看线程堆栈
- 查看 Bean 列表和环境变量
- 发送通知（邮件/钉钉/WebHook）当应用状态变化

## 注册方式

```xml
<!-- Admin Client 方式：主动注册 -->
<dependency>
    <groupId>de.codecentric</groupId>
    <artifactId>spring-boot-admin-starter-client</artifactId>
</dependency>
```

```yaml
spring:
  boot:
    admin:
      client:
        url: http://admin-server:9090
```

或者通过 Nacos/Eureka 自动发现（Admin Server 从注册中心拉取服务列表）。""",
        "历史,监控,Actuator,Admin Server",
    ),
]

ADMIN_INTERVIEWS = [
    (
        "Spring Boot Admin 和 Actuator 是什么关系？和 Prometheus 的区别？",
        """## Admin vs Actuator

**Actuator 提供数据，Admin 提供界面。**

- Actuator：暴露 `/actuator/health`、`/actuator/metrics` 等端点——这是**数据源**
- Admin Server：定时拉取 Actuator 端点数据，用 UI 面板展示——这是**可视化层**

Admin 不生成数据，只是数据的搬运工和展示者。

## Admin vs Prometheus

| 维度 | Spring Boot Admin | Prometheus + Grafana |
|------|------------------|---------------------|
| 定位 | 应用管理面板 | 指标监控 + 告警平台 |
| 数据获取 | 拉取 Actuator | 抓取 /actuator/prometheus |
| 数据存储 | 内存（不持久化）| TSDB（长期存储）|
| 告警 | 基础通知 | 强大的 PromQL + AlertManager |
| 适用场景 | 开发/测试环境快速查看 | 生产环境标准方案 |

> 两者不冲突：Admin 用于开发时快速排查问题，Prometheus+Grafana 用于生产环境的长期监控和告警。""",
        "Actuator,Prometheus,对比,监控",
    ),
]

TASK_NOTES = [
    (
        "Spring Cloud Task 的历史与定位",
        """## 是什么

Spring Cloud Task 是 2016 年发布的组件，专门用于**短生命周期微服务**（批处理任务、数据迁移、定时任务）。

普通微服务启动后一直在运行，Task 微服务执行完就退出。

## 适用场景

- 定时数据同步（每天凌晨从 A 库同步到 B 库）
- 报表生成（月底跑月报）
- 数据迁移（一次性迁移老数据）
- 批处理作业

## 和 Spring Batch 的关系

| 维度 | Spring Batch | Spring Cloud Task |
|------|-------------|------------------|
| 定位 | 批处理框架（读→处理→写）| 任务生命周期管理 |
| 关系 | Task 通常集成 Batch | 。|
| 提供能力 | ItemReader/Processor/Writer | 任务记录、执行状态持久化 |

## 任务记录

Task 自动记录每次运行的元数据：
```sql
TASK_EXECUTION 表：
  TASK_EXECUTION_ID | START_TIME | END_TIME | EXIT_CODE | EXIT_MESSAGE
  1                 | ...        | ...      | 0         | "SUCCESS"
```

这样你可以追踪每一次任务执行的起止时间、成功/失败、退出码等信息。""",
        "历史,定位,批处理,任务",
    ),
]

TASK_INTERVIEWS = [
    (
        "Spring Cloud Task 和 Spring Batch 有什么区别？什么时候用 Task？",
        """## 区别

**Batch 管"怎么处理"，Task 管"什么时候跑过、有没有失败"。**

Batch 的核心抽象：Reader → Processor → Writer。处理大批量数据的分段式处理。

Task 的核心价值：记录任务的**生命周期元数据**——什么任务、什么时间、执行了多长时间、成功还是失败。

## 什么时候用 Task

- 你的服务是"跑完就退出"的批处理服务
- 你需要在数据库中追踪每次任务执行的历史
- 你需要在 K8s 上把任务当 Job/CronJob 运行

## 什么时候只用 Batch

- 批处理逻辑复杂但不需要追踪执行历史
- 任务执行记录由外部系统（Jenkins/Argo Workflow）管理""",
        "Spring Batch,区别,批处理",
    ),
]

CONTRACT_NOTES = [
    (
        "Spring Cloud Contract 的历史与原理",
        """## 起源

Spring Cloud Contract 2016 年发布，实现了**消费者驱动契约测试**（Consumer-Driven Contracts, CDC）。

在微服务架构中，API 兼容性问题特别头痛：Provider 改了一个字段名，Consumer 调用就 500。Contract 的思路是：**让 Consumer 定义对 API 的期望，Provider 满足这些期望**。

## 工作流程

```
Consumer 侧：
  ① 定义契约（Groovy DSL / YAML）
     "当 GET /users/1 时，期望返回 {id: 1, name: 'Zhang San'}"
  ② push 契约到共享仓库

Provider 侧：
  ③ 拉取所有 Consumer 的契约
  ④ 运行契约测试（自动验证 API 是否符合契约）
  ⑤ 测试失败 → 说明改了 API 破坏了兼容性 → 不能上线
```

## 契约示例

```groovy
// contracts/shouldReturnUser.groovy
Contract.make {
    request {
        method 'GET'
        url '/users/1'
    }
    response {
        status 200
        body([
            id: 1,
            name: 'Zhang San'
        ])
        headers {
            contentType applicationJson()
        }
    }
}
```

## 为什么不用集成测试

集成测试 = Provider + Consumer + 真实数据库 → 慢、重、难维护

Contract 测试 = Provider 侧用 Mock 验证 API 格式 → 快、轻、精确。它验证的不是"业务逻辑是否正确"，而是"API 格式是否兼容"。""",
        "历史,CDC,契约测试,API兼容性",
    ),
]

CONTRACT_INTERVIEWS = [
    (
        "什么是消费者驱动契约测试？Spring Cloud Contract 解决了什么问题？",
        """## 传统的 API 测试困局

Provider 改了字段名（userName → name），自己跑测试全绿，但 Consumer 挂了。因为没有测试能提前发现"Provider 的变更加破坏了 Consumer 的期望"。

## Contract 的解法

让 Consumer 把自己对 API 的期望写成契约文件，Provider 在发版前自动验证是否满足所有 Consumer 的期望。

```
Consumer A: "GET /users/1 返回 {id, name}"   ┐
Consumer B: "GET /users/1 返回 {id, email}"  ├→ 契约仓库
Consumer C: "POST /users 接受 {name, age}"   ┘
                                                 │
Provider 发版前:                                    │
  运行 Contract 验证 ← 拉取所有契约 ←──────────────┘
  → 验证 A: ✅ 返回了 id 和 name
  → 验证 B: ❌ 缺少 email 字段 → 构建失败！
```

## 核心价值

- Provider 改 API 时，破坏了哪个 Consumer 的期望，立即知道
- Consumer 不需要启动 Provider 的真实实例，基于契约的 Stub 就能开发和测试
- 避免"集测环境谁都测不过"的困境""",
        "CDC,契约,API,测试",
    ),
]

# ====================================================================
# 数据组装与写入
# ====================================================================

ALL_DATA = {
    "Spring Cloud OpenFeign":             (FEIGN_NOTES, FEIGN_INTERVIEWS),
    "Spring Cloud LoadBalancer":          (LB_NOTES, LB_INTERVIEWS),
    "Spring Cloud Alibaba Sentinel":      (SENTINEL_NOTES, SENTINEL_INTERVIEWS),
    "Resilience4j":                       (RESILIENCE4J_NOTES, RESILIENCE4J_INTERVIEWS),
    "Spring Cloud Circuit Breaker":       (CB_NOTES, CB_INTERVIEWS),
    "Spring Cloud Gateway":               (GATEWAY_NOTES, GATEWAY_INTERVIEWS),
    "Spring Cloud Config":                (CONFIG_NOTES, CONFIG_INTERVIEWS),
    "Spring Cloud Bus":                   (BUS_NOTES, BUS_INTERVIEWS),
    "Spring Cloud Stream":                (STREAM_NOTES, STREAM_INTERVIEWS),
    "SkyWalking":                         (SKYWALKING_NOTES, SKYWALKING_INTERVIEWS),
    "Micrometer Tracing":                 (MICROMETER_NOTES, MICROMETER_INTERVIEWS),
    "Spring Cloud Alibaba Seata":         (SEATA_NOTES, SEATA_INTERVIEWS),
    "MyBatis-Plus":                       (MYBATIS_NOTES, MYBATIS_INTERVIEWS),
    "Spring Cloud Kubernetes":            (K8S_NOTES, K8S_INTERVIEWS),
    "Spring Boot Admin":                  (ADMIN_NOTES, ADMIN_INTERVIEWS),
    "Spring Cloud Task":                  (TASK_NOTES, TASK_INTERVIEWS),
    "Spring Cloud Contract":              (CONTRACT_NOTES, CONTRACT_INTERVIEWS),
}


def seed():
    db = get_db()
    total_notes = total_interviews = 0

    for stack_name, (notes, interviews) in ALL_DATA.items():
        row = db.execute("SELECT id FROM stack WHERE name = ?", (stack_name,)).fetchone()
        if not row:
            print(f"  SKIP {stack_name}: not found")
            continue
        sid = row["id"]
        db.execute("DELETE FROM entry WHERE stack_id = ?", (sid,))

        for title, content, tags in notes:
            db.execute(
                "INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?,?,?,?,'note')",
                (sid, title, content, tags),
            )
        for title, content, tags in interviews:
            db.execute(
                "INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?,?,?,?,'interview')",
                (sid, title, content, tags),
            )

        db.commit()
        print(f"  OK {stack_name}: {len(notes)} notes + {len(interviews)} interviews")
        total_notes += len(notes)
        total_interviews += len(interviews)

    db.close()
    print(f"\nTotal: {total_notes} notes + {total_interviews} interviews across {len(ALL_DATA)} stacks")


if __name__ == "__main__":
    seed()
