"""Dubbo 各技术栈的知识笔记和面试题内容"""
from db import get_db

DATA = {
    "Dubbo 概述与 RPC 原理": (
        [
            (
                "Dubbo 的历史与发展",
                """## 起源

Dubbo 最初由**阿里巴巴**的梁飞（@lianfei）在 2008 年开发，2009 年正式对外开源。当时淘宝从 PHP 转向 Java，服务数量爆炸式增长，急需一个高性能的 RPC 框架。

**命名**：Dubbo 的名字来源于梁飞养的猫叫"Dubbo"（多宝）。

## 关键时间线

| 时间 | 事件 |
|------|------|
| 2008 | 梁飞开始开发 Dubbo，内部代号 Dubbo |
| 2011 | 阿里将 Dubbo 捐给 Apache，进入 Apache 孵化器（但进程缓慢）|
| 2014 | Dubbo 社区几乎停更，阿里内部用 HSF 替代 |
| 2017 | Dubbo 浴火重生！阿里巴巴重启 Dubbo 维护，正式捐给 Apache |
| 2018.02 | Dubbo 正式从 Apache 毕业，成为顶级项目 |
| 2019.05 | Dubbo 2.7.0 发布，异步编程模型重构 |
| 2021.06 | Dubbo 3.0 发布，应用级服务发现、Triple 协议 |
| 2023+ | Dubbo 3.x 持续迭代，云原生方向 |

## 什么是 RPC

RPC（Remote Procedure Call）= 像调本地方法一样调远程服务。

```
Client 调用: userService.getUser(1L)  ← 感觉像调本地方法
    │
    │ 实际发生了什么：
    ├→ 1. Client Stub：把方法调用序列化为二进制（序列化）
    ├→ 2. Transport：通过网络发送数据（TCP/UDP/HTTP）
    ├→ 3. Server Stub：反序列化为 Java 对象
    ├→ 4. 调用真正的 UserService.getUser(1L)
    ├→ 5. 返回值序列化 → 回传 → 反序列化
    └→ 6. 返回给 Client
```

## Dubbo 的核心设计理念

Dubbo 的定位不是"另一个 HTTP 框架"，而是**面向接口的 RPC 框架**：

- **接口即契约**：服务提供者和消费者共享同一个 Java 接口
- **透明化远程调用**：开发者和本地调用几乎一样的体验
- **插件化架构**：几乎所有组件都可以通过 SPI 替换""",
                "历史,RPC,演进,起源,核心概念",
            ),
            (
                "Dubbo 核心架构与工作流程",
                """## 核心角色

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Registry  │     │   Monitor    │     │   Consumer   │
│  (注册中心)   │     │  (监控中心)   │     │  (服务消费者) │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                   │                    │
 ①注册  │           ③统计上报│                    │②订阅
       │                   │                    │
┌──────┴───────────────────┴────────────────────┴───────┐
│                     Provider (服务提供者)               │
└──────────────────────────────────────────────────────┘
```

## RPC 调用全流程

```
Consumer                                                  Provider
   │                                                           │
   │─① 从 Registry 订阅服务，获取 Provider 地址列表────────────→│
   │                                                           │
   │─② 调用 userService.getUser(1L)                             │
   │    ├→ 生成 RpcInvocation（方法名、参数、返回值类型）         │
   │    ├→ Router：过滤路由规则                                  │
   │    ├→ LoadBalance：选一个 Provider 实例                     │
   │    ├→ Filter Chain：执行过滤器链（监控、限流、鉴权...）       │
   │    ├→ Protocol：序列化 + 发送网络请求 ─────────────────→    │
   │                                                           │
   │                                                         ③收到请求
   │                                                           ├→ Protocol：反序列化
   │                                                           ├→ Filter Chain
   │                                                           ├→ 反射调用真正的 UserService
   │                                                           ├→ 返回结果 ←── Protocol 序列化
   │                                                           │
   │   ←── 反序列化返回结果 ─────────────────────────────────    │
   │                                                           │
   │─④ Monitor：上报调用统计（RT、QPS、成功/失败）                │
```

## 核心模块

| 模块 | 职责 | 可替换实现 |
|------|------|-----------|
| **Registry** | 注册中心，服务地址的发布与订阅 | ZooKeeper / Nacos / Redis / Consul |
| **Protocol** | 通信协议，远程调用的序列化和传输 | dubbo:// / triple:// / rest:// / grpc:// |
| **Proxy** | 代理工厂，生成服务的本地代理对象 | Javassist / JDK 动态代理 |
| **Cluster** | 集群容错，失败后的处理策略 | Failover / Failfast / Failsafe |
| **LoadBalance** | 负载均衡，从多个 Provider 中选一个 | Random / RoundRobin / ConsistentHash |
| **Router** | 路由，按规则过滤 Provider 列表 | ConditionRouter / TagRouter |
| **Filter** | 过滤器链，调用前后的拦截处理 | MonitorFilter / TpsLimitFilter |
| **Monitor** | 监控，调用次数、RT、成功率统计 | Dubbo Monitor / Prometheus |""",
                "架构,工作流程,角色,核心模块,RPC",
            ),
        ],
        [
            (
                "什么是 RPC？RPC 和 HTTP 有什么区别？为什么 Dubbo 选择 RPC？",
                """## RPC 的本质

RPC 的目的是让远程调用像本地调用一样简单。底层封装了网络通信的复杂性。

## RPC vs HTTP

| 维度 | RPC (Dubbo) | HTTP (Spring Cloud) |
|------|------------|-------------------|
| **协议** | 自定义二进制协议（TCP 长连接）| HTTP/1.1 文本协议 |
| **序列化** | 高效二进制（Hessian2/Protobuf）| JSON/XML（文本，体积大）|
| **性能** | 高（TCP 长连接 + 二进制）| 较低（HTTP 每次请求建连 + JSON 序列化开销大）|
| **服务定义** | Java 接口共享 | RESTful API（不共享代码）|
| **跨语言** | 需多语言 SDK（Dubbo Go/JS/Python）| 天然跨语言 |
| **调试** | 不便（二进制不可读）| 方便（curl/浏览器）|
| **生态** | 国内为主 | 全球通用 |

## 为什么 Dubbo 用 RPC

1. **性能要求**：阿里内部服务间调用量巨大，HTTP 的 JSON 序列化和短连接开销不可接受
2. **面向接口编程**：Java 接口是天然的 API 定义，Provider 和 Consumer 共享接口避免歧义
3. **服务治理能力**：RPC 层可以做更细粒度的流量控制和调用统计

> 面试金句：RPC = 像调本地方法一样调远程，HTTP = 像访问网页一样调接口。前者是面向接口的，后者是面向资源的。""",
                "RPC,HTTP,对比,原理,高频",
            ),
            (
                "Dubbo 服务调用的一次完整 RPC 流程是怎样的？",
                """## 完整调用链

从 Consumer 调用到 Provider 返回，经过的组件依次为：

```
Consumer 端：
  ① Proxy（代理层）→ 生成接口的代理对象
  ② Cluster（集群层）→ 选择一个集群策略
  ③ Directory（目录服务）→ 提供可用 Provider 列表
  ④ Router（路由层）→ 按路由规则过滤
  ⑤ LoadBalance（负载均衡）→ 选一个具体实例
  ⑥ Filter Chain → 执行 Consumer 端过滤器
  ⑦ Protocol → 序列化 + 网络发送

网络传输（TCP 长连接）

Provider 端：
  ⑧ Protocol → 反序列化
  ⑨ Filter Chain → 执行 Provider 端过滤器
  ⑩ 反射调用 → 找到真正的实现类并 invoke
  ⑪ 返回值 → 序列化 → 回传
```

## 每个步骤的职责

| 步骤 | 职责 | 典型问题 |
|------|------|---------|
| Proxy | 让 Consumer 以为在调本地方法 | JDK Proxy vs Javassist 哪个快？|
| Cluster | 集群调用失败怎么办？| Failover 重试次数设多少？|
| Directory | 哪些 Provider 可用？| 服务列表如何维护？|
| Router | 这个请求该打到哪个机房？| 同机房优先怎么写？|
| LoadBalance | 选了 3 台，打哪一台？| 加权随机 vs 最少活跃？|
| Filter | 统计/鉴权/限流怎么做？| MonitorFilter 的性能开销？|
| Protocol | TCP 协议要怎么定？| Dubbo vs Triple 怎么选？|

> 面试加分点：能说出这 10 个步骤的组件名和职责，说明你对 Dubbo 不只是会用，而是真懂原理。""",
                "调用流程,架构,组件,链式调用,高频",
            ),
        ],
    ),
    "Dubbo 服务注册与发现": (
        [
            (
                "Dubbo 服务注册发现机制",
                """## 服务注册流程

```
Provider 启动
    │
    ├→ ServiceConfig.export() 导出服务
    ├→ 构建 URL: dubbo://192.168.1.10:20880/com.example.UserService?...
    ├→ Protocol.export() 启动 Netty Server，监听 20880 端口
    └→ Registry.register(url) 向注册中心写入临时节点
         │
         ├── ZooKeeper: /dubbo/com.example.UserService/providers/dubbo%3A%2F%2F192.168...
         ├── Nacos: 注册为临时实例
         └── Redis: 存入 Set 集合
```

## 服务发现流程

```
Consumer 启动
    │
    ├→ ReferenceConfig.get() 获取服务代理
    ├→ Registry.subscribe(url) 订阅服务
    └→ RegistryDirectory.notify(providerUrls)
         │
         ├→ ① 拉取全量 Provider 地址列表
         ├→ ② 注册 Watcher（ZooKeeper）或长连接（Nacos）
         └→ ③ Provider 上线/下线 → 收到变更通知 → 更新本地列表
```

## 注册中心对比

| 注册中心 | 一致性 | 优势 | 劣势 |
|---------|-------|------|------|
| **ZooKeeper** | CP | 生态成熟，Dubbo 默认 | 强一致性导致可用性低 |
| **Nacos** | AP+CP | 一站式（注册+配置）| 较新，部分公司未推广 |
| **Redis** | 最终一致性 | 轻量，已有基础设施 | 无 Watcher，靠轮询 |
| **Consul** | CP | 健康检查强 | 国内用得少 |

## 服务注册数据

注册到中心的 URL 示例：
```
dubbo://192.168.1.10:20880/com.example.UserService
  ?anyhost=true
  &application=user-provider
  &dubbo=2.7.8
  &interface=com.example.UserService
  &methods=getUser,listUsers
  &pid=12345
  &side=provider
  &timestamp=1620000000000
```

包含了 IP、端口、接口名、方法列表、版本号等全部元数据。""",
                "注册,发现,Registry,ZooKeeper,Nacos",
            ),
        ],
        [
            (
                "Dubbo 的注册中心挂了还能继续调用吗？",
                """## 答案：可以

Dubbo Consumer 在首次订阅后将 Provider 地址列表**缓存在本地**。注册中心挂掉期间：

1. Consumer 使用本地缓存的地址列表继续调用
2. 注册中心恢复后自动重新连接、重新订阅

这得益于 Dubbo 的 **RegistryDirectory** 设计，它维护了一个本地 Provider 列表，注册中心只是数据来源之一。

## 但有限制

- 注册中心挂掉期间，**新的 Provider 无法被 Consumer 发现**
- 已经下线的 Provider 仍在 Consumer 的本地缓存中，可能调用失败
- 调用失败后，Cluster 容错机制（如 Failover）会尝试下一个 Provider

> 所以可以说：注册中心挂了不影响**存量调用**，但影响**服务变更的感知**。""",
                "注册中心,高可用,缓存,Registry",
            ),
        ],
    ),
    "Dubbo 通信协议": (
        [
            (
                "Dubbo 协议家族与设计原理",
                """## Dubbo 支持的协议

| 协议 | 特点 | 适用场景 |
|------|------|----------|
| **dubbo://** | 单一 TCP 长连接 + NIO 异步，Hessian2 序列化 | Dubbo 原生，服务间调用首选 |
| **triple://** | 基于 HTTP/2 + Protobuf，兼容 gRPC | Dubbo 3.x 默认，跨语言互调 |
| **rest://** | HTTP RESTful，JSON 序列化 | 对外暴露 API，浏览器可调 |
| **grpc://** | gRPC 协议 | 与 gRPC 生态互通 |
| **hessian://** | Hessian RPC | 集成旧系统 |
| **redis://** | Redis 协议 | 极端简单的 RPC |
| **rmi://** | Java RMI | 纯 Java 环境 |

## Dubbo 协议的原理（dubbo://）

```
┌──────────────────────────────────────┐
│        Dubbo 协议帧结构                 │
├────┬────┬────────────────────────────┤
│ 头  │ 头   │         Body             │
│Magic│Flags│        Payload            │
│2B   │ ?B  │                          │
│0xdabb│     │                          │
└────┴────┴────────────────────────────┘

Header（16 字节）:
  Magic (2B):         0xdabb
  Serialization (1B): 2=Hessian2
  Request/Response (1B)
  Status (1B):       20=OK
  Request ID (8B):   请求唯一 ID
  Body Length (4B):  Body 长度
```

- **Magic 0xdabb**：协议标识，"dubb" 的变形
- **单一长连接**：Consumer → Provider 之间只建一条 TCP 连接，多路复用
- **异步非阻塞 IO**：基于 Netty NIO，少量线程处理大量连接

## Dubbo vs Triple 协议对比

| 维度 | Dubbo | Triple |
|------|-------|--------|
| 传输层 | TCP 自定义 | HTTP/2 |
| 序列化 | Hessian2 | Protobuf（默认）|
| 多路复用 | 连接级（Request ID）| 流级（Stream）|
| 跨语言 | 需 Dubbo 多语言 SDK | 兼容 gRPC 生态 |
| 流式调用 | 不支持 | ✅ 支持（Server Stream / Client Stream / Bidirectional Stream）|
| 穿透网关 | 需协议转换 | HTTP/2 天然可穿透 |

> 趋势：Dubbo 3.x 中 Triple 成为默认协议，逐步替代 Dubbo 协议。新项目直接上 Triple。""",
                "协议,frame,dubbo协议,Triple,对比",
            ),
        ],
        [
            (
                "Dubbo 协议和 Triple 协议的区别？3.x 为什么用 Triple？",
                """## 核心区别

Dubbo 协议是阿里自研的**私有二进制协议**，基于 TCP + Request ID 多路复用。

Triple 协议基于 **HTTP/2 + Protobuf**，是 Dubbo 3.x 引入的开放协议。

## 为什么 3.x 推 Triple

1. **云原生友好**：HTTP/2 可以穿透 K8s Ingress、Service Mesh（Envoy/Istio），Dubbo 协议是私有二进制，网关不认识
2. **跨语言互通**：Triple 兼容 gRPC 协议，Go/Python/Node.js 的原生 gRPC SDK 可以直接调 Dubbo 服务
3. **流式调用支持**：Dubbo 协议不支持 Streaming，Triple 支持 Client Stream / Server Stream / Bidirectional Stream
4. **微服务标准化**：社区在向 gRPC/HTTP2 收敛，Dubbo 不能孤立

## 选型建议

- 新项目 → Triple（默认）
- 内部纯 Java → Dubbo 协议性能更高（少数场景）
- 需要穿透网关/Mesh → Triple""",
                "Triple,Dubbo协议,对比,HTTP2,高频",
            ),
        ],
    ),
    "Dubbo 序列化机制": (
        [
            (
                "Dubbo 序列化方案全对比",
                """## 序列化在 RPC 中的位置

```
Java 对象 → 序列化 → 字节流 → 网络传输 → 字节流 → 反序列化 → Java 对象
```

## Dubbo 支持的序列化方案

| 方案 | 类型 | 性能 | 大小 | 跨语言 | Dubbo 版本 |
|------|------|------|------|--------|-----------|
| **Hessian2** | 二进制 | 中 | 中 | ✅ | 2.x 默认 |
| **FastJSON2** | JSON | 高 | 较大 | ✅ | 3.x 默认 |
| **Protobuf** | 二进制 | 很高 | 很小 | ✅ | 推荐 |
| **Kryo** | 二进制 | 很高 | 很小 | ❌ Java only |
| **FST** | 二进制 | 很高 | 小 | ❌ Java only |
| **JDK Serializable** | 二进制 | 慢 | 大 | ❌ | 不推荐 |

## Hessian2 的问题

Hessian2 是 Dubbo 2.x 的默认序列化，但有几个问题：

1. **跨语言支持弱**：Hessian2 的 Go/JS 实现不完善
2. **对象兼容性差**：字段增删容易导致反序列化失败
3. **性能瓶颈**：比 Protobuf 慢 3-5 倍

## FastJSON2 → Dubbo 3.x 的选择

Dubbo 3.x 默认用 FastJSON2（阿里开源的高性能 JSON 库），原因是：
- JSON 可读性好，调试方便
- 性能不亚于 Protobuf（FastJSON2 有大量优化）
- 比 Hessian2 的跨语言支持更好

> 选型：API 对外 → JSON；内部高性能 → Protobuf/Kryo；兼容旧系统 → Hessian2。""",
                "序列化,Hessian2,FastJSON2,Protobuf,对比",
            ),
        ],
        [],
    ),
    "Dubbo 集群容错": (
        [
            (
                "Dubbo 六大集群容错策略",
                """## 什么是集群容错

当 Consumer 调用 Provider 失败时，Dubbo 如何处理？

## 六大策略

| 策略 | 行为 | 适用场景 |
|------|------|----------|
| **Failover** | 失败自动切换，重试其他 Provider（默认）| 读操作（幂等）|
| **Failfast** | 快速失败，立即抛异常 | 写操作（非幂等）|
| **Failsafe** | 安全失败，吞掉异常记录日志 | 日志/审计（不重要）|
| **Failback** | 失败后后台定时重试 | 消息通知（最终一致性）|
| **Forking** | 并行调多个 Provider，取第一个返回 | 实时性要求极高（牺牲资源）|
| **Broadcast** | 逐个调用所有 Provider，有一个失败即失败 | 通知所有 Provider（如缓存刷新）|

## Failover 配置

```xml
<dubbo:service cluster="failover" retries="2" />
```

重试 2 次 = 最多执行 3 次。Consumer 换一个 Provider 重试。

> ⚠️ 注意：幂等读操作最适合 Failover。对写操作用 Failover 可能导致重复写入！

## 源码要点

```java
// FailoverClusterInvoker.doInvoke()
for (int i = 0; i <= retries; i++) {
    Invoker<T> invoker = select(loadbalance, invocation, invokers, invoked);
    try {
        Result result = invoker.invoke(invocation);
        return result;
    } catch (RpcException e) {
        if (i >= retries) throw e;  // 重试耗尽
        // 记录异常，继续重试
    }
}
```""",
                "集群,容错,Failover,Failfast,策略",
            ),
        ],
        [
            (
                "Dubbo 的 Failover 和 Failfast 有什么区别？重试会有什么问题？",
                """## 区别

- **Failover**：失败了换一台 Provider 重试。适合读操作。默认重试 2 次。
- **Failfast**：失败了直接抛异常。适合写操作。

## 重试的坑

**1. 写操作幂等性问题**

`POST /order/create` 被重试了 3 次 → 创建了 3 笔订单！

解决方法：
- 写接口用 Failfast
- 或者接口实现幂等（用唯一业务 ID 去重）

**2. 超时累加**

设了 `timeout=1000ms`，`retries=2` → 最坏情况等待 3×1000 = 3 秒。要及时设置合理的超时。

**3. 下游压力放大**

Provider 已经扛不住了，Consumer 还不断换台机器重试 → 加剧雪崩。

解决方法：配置 `retries=0` + 配合 Sentinel 做熔断。""",
                "Failover,Failfast,重试,幂等,高频",
            ),
        ],
    ),
    "Dubbo 负载均衡": (
        [
            (
                "Dubbo 四种负载均衡策略详解",
                """## 四种策略

| 策略 | 原理 | 适用场景 |
|------|------|----------|
| **Random** | 随机选一个（默认），支持加权 | 通用 |
| **RoundRobin** | 轮询，支持加权 | 请求均匀分发 |
| **LeastActive** | 选"最不忙"的 Provider（活跃请求最少）| 请求耗时差异大 |
| **ConsistentHash** | 同参数请求打到同一 Provider | 有状态服务 / 缓存 |

## Random（加权随机）

```
Provider A: weight=200 → 概率 200/(200+100+100) = 50%
Provider B: weight=100 → 概率 25%
Provider C: weight=100 → 概率 25%
```

## LeastActive（最少活跃调用数）

```
Provider A: active=5  ← 有 5 个正在处理的请求
Provider B: active=2  ← 最不忙，选它！
Provider C: active=8

活跃数 = 收到请求但还没返回的数量
LeastActive 的前提：每个请求的响应时间差不多
```

## ConsistentHash（一致性哈希）

```
hash(userId) % 2^32 → 落在哈希环上某个位置
    → 顺时针找最近的 Provider
    → 同一 userId 总是打到同一台机器

新增/移除 Provider 时只影响一部分请求，不会全量重新分配
```

适用：有本地缓存的场景（同一个 userId 的请求应该打到同一台机器，缓存命中率高）。

## 配置方式

```xml
<dubbo:service loadbalance="leastactive" />
<dubbo:reference loadbalance="consistenthash" />
```""",
                "负载均衡,Random,RoundRobin,LeastActive,ConsistentHash",
            ),
        ],
        [],
    ),
    "Dubbo 服务路由与治理": (
        [
            (
                "Dubbo 路由规则与灰度发布",
                """## 路由规则的作用

在 LoadBalance 之前先过滤 Provider 列表：

```
全量 Provider 列表 [A, B, C, D, E, F]
    │
    ├→ Condition Router（条件路由）
    │   如：host != 10.20.153.* → 排除某个机房的机器
    │   结果：[A, B, C, D]
    │
    ├→ Tag Router（标签路由）
    │   如：tag = gray → 只留灰度节点
    │   结果：[D]
    │
    └→ LoadBalance
        从 [D] 中选一个（没得选）
```

## 条件路由示例

```yaml
# 排除 192.168.1.10 这台机器
scope: service
force: true
runtime: true
conditions:
  - host != 192.168.1.10
```

## 灰度发布（标签路由）

```
                       ┌─→ Provider v1 (tag=stable)
Consumer (tag=gray) ───┤
                       └─→ Provider v2 (tag=gray)   ← 灰度 Consumer 只调灰度 Provider
```

```yaml
# Consumer 端配置
dubbo:
  consumer:
    tag: gray   # 标记为灰度消费者
```

Provider 端：
```yaml
dubbo:
  provider:
    tag: gray   # 标记为灰度提供者
```

## 动态配置

```yaml
# 通过 Dubbo Admin 控制台动态下发，无需重启
configVersion: v3.0
scope: service
key: com.example.UserService
configs:
  - addresses: ["192.168.1.10:20880"]
    side: provider
    parameters:
      weight: 50   # 降权 → 引流
```""",
                "路由,灰度发布,标签,治理,动态配置",
            ),
        ],
        [
            (
                "Dubbo 怎么做灰度发布？标签路由的原理是什么？",
                """## 标签路由原理

Dubbo 的标签路由（TagRouter）通过给 Provider 打标签，Consumer 带标签，实现流量隔离：

```
Consumer A (env=gray)  ──→  Provider A (env=gray)
Consumer B (env=gray)  ──→  Provider B (env=gray)
Consumer C (env=prod)  ──→  Provider C (env=prod)
Consumer D (env=prod)  ──→  Provider D (env=prod)
```

如果灰度 Consumer 找不到灰度 Provider → 降级调用生产 Provider（可配置）。

## 灰度发布步骤

1. 部署灰度 Provider（tag=gray）
2. 用 Dubbo Admin 下发动调路由规则
3. 少量 Consumer 打上 tag=gray 标签（或者通过路由规则按 IP 匹配）
4. 灰度流量打到灰度节点
5. 验证 OK → 全量上线 → 去掉路由规则""",
                "灰度,标签路由,TagRouter,高频",
            ),
        ],
    ),
    "Dubbo SPI 扩展机制": (
        [
            (
                "Dubbo SPI 扩展机制深度解析",
                """## 什么是 SPI

SPI（Service Provider Interface）= **接口 + 实现 + 配置文件 = 插件化**

Java 自带了 SPI（`META-INF/services/`），但 Dubbo 重写了一套更强的 SPI。

## Dubbo SPI vs Java SPI

| 维度 | Java SPI | Dubbo SPI |
|------|----------|-----------|
| 加载方式 | 一次性加载全部实现 | 按需加载 |
| 获取方式 | `ServiceLoader.iterator()` | `ExtensionLoader.getExtension("name")` |
| AOP | ❌ | ✅ Wrapper 类自动包装 |
| IOC | ❌ | ✅ 自动注入依赖 |
| 配置文件位置 | `META-INF/services/` | `META-INF/dubbo/` / `META-INF/dubbo/internal/` |

## Dubbo SPI 示例

```java
// 1. 定义接口
@SPI("dubbo")  // 默认实现为 dubbo
public interface Protocol {
    void export(Invoker<?> invoker);
}

// 2. 实现
public class DubboProtocol implements Protocol { ... }
public class TripleProtocol implements Protocol { ... }
public class RestProtocol implements Protocol { ... }

// 3. 配置文件：META-INF/dubbo/internal/com.xxx.Protocol
dubbo=com.xxx.DubboProtocol
triple=com.xxx.TripleProtocol
rest=com.xxx.RestProtocol

// 4. 使用
Protocol protocol = ExtensionLoader.getExtensionLoader(Protocol.class)
    .getExtension("triple");  // 按名称获取
```

## Wrapper 机制（AOP）

```java
// ProtocolFilterWrapper 包装了所有 Protocol 实现
// 对 Protocol 加 filterChain，不需要修改每个 Protocol 实现
public class ProtocolFilterWrapper implements Protocol {
    private Protocol protocol;  // 被包装的真正 Protocol

    public void export(Invoker<?> invoker) {
        // 先加 filter 链，再调用真正的 export
        return protocol.export(buildFilterChain(invoker));
    }
}
```

## Adaptive Extension（适配扩展）

```java
@Adaptive
public class AdaptiveProtocol implements Protocol {
    public void export(Invoker<?> invoker) {
        // 根据 URL 中的参数决定用哪个实现
        String extName = invoker.getUrl().getParameter("protocol", "dubbo");
        Protocol protocol = ExtensionLoader.getExtension(extName);
        protocol.export(invoker);
    }
}
```

> 面试金句：Dubbo 的 SPI 是 Dubbo 微内核架构的基石。Dubbo 功能强大不是因为代码多，而是因为几乎所有组件都可以被替换。""",
                "SPI,ExtensionLoader,插件,微内核,Wrapper",
            ),
        ],
        [
            (
                "Dubbo 的 SPI 和 Java SPI 有什么区别？为什么 Dubbo 自己要重写一套？",
                """## 核心区别

Java SPI 是**全量加载**，Dubbo SPI 是**按需加载 + AOP + IOC**。

## Dubbo 重写的原因

1. **按需加载**：Java SPI 把 META-INF/services 下所有实现类都实例化，浪费资源。Dubbo SPI 只在真正 `getExtension("name")` 时才加载。

2. **AOP 增强**：Dubbo SPI 的 Wrapper 类可以自动包装原始实现（如 ProtocolFilterWrapper 给 Protocol 加 filter 链），不用改原始代码。

3. **IOC 注入**：Dubbo SPI 自动把依赖注入到扩展实现中。

4. **Adaptive 机制**：根据 URL 参数动态选择使用哪个实现（如 `?protocol=triple` → 用 TripleProtocol）。

## 一句话

> Java SPI = 穷举所有可能；Dubbo SPI = 按需索取 + 自动增强。""",
                "SPI,Java SPI,对比,AOP,IOC,高频",
            ),
        ],
    ),
    "Dubbo 异步调用与泛化调用": (
        [
            (
                "Dubbo 异步调用详解",
                """## 异步调用的三种方式

### 1. Future 异步（2.7 之前）

```java
// 配置：async=true
@DubboReference(async = true)
private UserService userService;

UserService.sayHello("world");
Future<User> future = RpcContext.getContext().getFuture();
User user = future.get();  // 阻塞等待结果
```

### 2. CompletableFuture（2.7+，推荐）

```java
@DubboReference
private UserService userService;

CompletableFuture<User> future = userService.getUserAsync(1L);
future.thenAccept(user -> {
    System.out.println("Got user: " + user.getName());
});
```

### 3. Reactor 响应式（3.x+）

```java
@DubboReference
private UserService userService;

Mono<User> mono = userService.getUserMono(1L);
mono.flatMap(user -> ...)
    .subscribe();
```

## 泛化调用

**不需要引入 Provider 的 API jar 包就能调用！**

```java
// Consumer 不需要 import User 类！
GenericService userService = ReferenceConfig.getGenericService("com.example.UserService");

// 泛化方式调用
Object result = userService.$invoke("getUser",
    new String[]{"java.lang.Long"},
    new Object[]{1L});

// 结果转为 Map
Map<String, Object> userMap = (Map<String, Object>) result;
System.out.println(userMap.get("name"));
```

泛化调用的用途：
- API 网关：网关不引入任何业务服务的 jar，用泛化调用来转发
- 测试平台：动态调用任意服务，不用编译
- 服务 Mock：测试时不依赖真实的 Provider

## 异步调用 vs 同步调用

| 维度 | 同步 | 异步 |
|------|------|------|
| 线程模型 | 业务线程阻塞等待 | IO 线程回调，业务线程不阻塞 |
| 吞吐量 | 低 | 高 |
| 代码复杂度 | 低 | 中（回调地狱 → CompletableFuture → Reactive）|
| 调试 | 简单 | 难（堆栈不同）|""",
                "异步,Future,CompletableFuture,泛化调用,Reactor",
            ),
        ],
        [],
    ),
    "Dubbo 线程模型与性能优化": (
        [
            (
                "Dubbo 线程派发模型",
                """## Dubbo 的线程池分类

Dubbo 在 Provider 端有**两类线程**：

```
请求到达 → Netty IO 线程池 (boss + worker)
              │
              ↓ 反序列化后
        业务线程池 (DubboServerHandler 线程池)
              │
              ↓ 反射调用
        真正的 Service 实现
```

## 四种线程派发策略

| 策略 | 行为 |
|------|------|
| **all（默认）** | 所有请求都在业务线程池处理 |
| **direct** | 所有请求直接在 IO 线程处理（不切换线程，延迟最低但阻塞 IO）|
| **message** | 只有请求在业务线程池，响应在 IO 线程 |
| **execution** | 只有请求在业务线程池，其他在 IO 线程 |
| **connection** | 连接事件在 IO 线程 |

```xml
<dubbo:protocol name="dubbo" dispatcher="all" threadpool="fixed" threads="200" />
```

## 线程池类型

| 类型 | 说明 |
|------|------|
| **fixed** | 固定大小线程池（默认，200 线程）|
| **cached** | 缓存线程池，空闲 1 分钟回收 |
| **limited** | 可伸缩线程池，只增不减 |
| **eager** | 优先创建新线程而非排队 |

## 性能优化要点

```yaml
dubbo:
  provider:
    threads: 200          # 业务线程池大小（默认 200）
    queues: 0             # 队列大小（0 = 同步队列，满则创建新线程）
    iothreads: 8          # IO 线程数（默认 CPU+1）
    payload: 8388608      # 最大请求大小 8MB
    serialization: protobuf  # 高性能序列化
    connections: 1        # 每个 Provider 的连接数（单一长连接）
```

> 调优口诀：IO 线程 = CPU+1，业务线程 = 根据下游 RT 和 QPS 计算（QPS × RT / 1000）。""",
                "线程模型,线程池,性能,调优,dispatcher",
            ),
        ],
        [],
    ),
    "Dubbo Admin 控制台": (
        [
            (
                "Dubbo Admin 的部署与功能",
                """## Dubbo Admin 是什么

Dubbo Admin 是 Dubbo 的**官方管理控制台**，可视化地管理和监控 Dubbo 服务。

## 核心功能

- **服务查询**：查看所有已注册的服务、Provider、Consumer
- **服务治理**：动态修改路由规则、权重、负载均衡策略
- **流量控制**：配合 Sentinel 做限流降级
- **监控统计**：查看调用次数、RT、成功率
- **配置管理**：动态修改服务参数（timeout、retries 等）

## 部署

```bash
# Docker 方式
docker run -p 8080:8080 \
  -e admin.registry.address=zookeeper://zk-server:2181 \
  apache/dubbo-admin
```

访问 `http://localhost:8080`，默认账号 root/root。

## 常用操作

1. **动态调整权重**：在控制台找到 Provider → 修改权重 → 生效（无需重启）
2. **启用/禁用服务**：在控制台直接操作，让 Provider 不再接受流量
3. **查看路由规则**：检查当前生效的路由规则
4. **查看服务调用关系**：哪些 Consumer 调了哪些 Provider""",
                "Admin,控制台,部署,治理",
            ),
        ],
        [],
    ),
    "Dubbo 3.x 核心新特性": (
        [
            (
                "Dubbo 3.0 架构重构与应用级服务发现",
                """## Dubbo 3.0 三大变革

### 1. 应用级服务发现（从接口级 → 应用级）

| 维度 | 2.x（接口级）| 3.x（应用级）|
|------|-----------|------------|
| 注册粒度 | 每个接口一条注册记录 | 每个应用一条注册记录 |
| 注册中心数据量 | O(接口数) | O(应用数) |
| 元数据存储 | 注册中心（URL 参数）| 元数据中心（独立存储）|
| 对大集群的影响 | 注册中心压力大（几十万条数据）| 轻量（几千条）|

```
2.x: /dubbo/com.example.UserService/providers/
     /dubbo/com.example.OrderService/providers/   ← 每个接口一个节点

3.x: /dubbo/user-provider/providers/192.168.1.10   ← 整个应用一个节点
         ↑
         元数据中心里查这个应用提供了哪些服务
```

### 2. Triple 协议

基于 gRPC + Protobuf，支持流式调用，兼容 gRPC 生态。

### 3. 云原生增强

- 原生支持 K8s Service 作为注册中心
- 支持 xDS 协议（与 Istio 集成）
- 支持 Proxyless Service Mesh

## 接口级 vs 应用级注册量对比

```
场景: 100 个应用，每个应用 50 个接口

2.x 接口级:    100 × 50 = 5000 条注册数据
3.x 应用级:    100       = 100 条注册数据
             ↓ 减少了 98% 的数据量

在大规模集群（万级接口）中，这是注册中心能否扛住的本质区别
```""",
                "3.0,应用级服务发现,Triple,架构,重构",
            ),
        ],
        [
            (
                "Dubbo 3.x 的「应用级服务发现」和 2.x 的「接口级」有什么区别？为什么要改？",
                """## 核心区别

2.x 接口级：注册中心里存的是"这个 Provider 提供了什么接口"
3.x 应用级：注册中心里存的是"这个应用在这里"；它提供了哪些接口存在**元数据中心**里

## 为什么要改

1. **注册中心压力**：100 个应用 × 50 个接口 = 5000 条注册数据。2.x 的注册中心存了太多 URL 字符串，数据膨胀严重。
2. **推送风暴**：Consumer 订阅 500 个接口 → 每个接口变化都要被通知 → 注册中心推送量大
3. **云原生对齐**：K8s Service 是应用级的，Istio 也是应用级的，Dubbo 用接口级则无法对齐

## 一句话

> 从"注册中心存所有细节"变成"注册中心只存应用位置，细节存元数据中心"。这是 Dubbo 从服务框架走向云原生基础设施的标志性转变。""",
                "应用级,接口级,注册中心,3.x,高频",
            ),
        ],
    ),
    "Dubbo + Sentinel 流量控制": (
        [
            (
                "Dubbo 集成 Sentinel 实现限流降级",
                """## 为什么 Dubbo 需要 Sentinel

Dubbo 本身有集群容错（Failover/Failfast），但没有**流量控制**和**熔断降级**能力。Sentinel 正好补齐这一块。

## 集成方式

```xml
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo-sentinel-spring-boot-starter</artifactId>
</dependency>
```

## 配置流控规则

```java
// 对 UserService.getUser 方法限流：QPS 不超过 100
FlowRule rule = new FlowRule();
rule.setResource("com.example.UserService:getUser()");
rule.setCount(100);
rule.setGrade(RuleConstant.FLOW_GRADE_QPS);
FlowRuleManager.loadRules(Collections.singletonList(rule));
```

## 配置熔断降级

```java
DegradeRule rule = new DegradeRule();
rule.setResource("com.example.UserService:getUser()");
rule.setCount(0.5);  // 50% 异常率 → 熔断
rule.setTimeWindow(10);  // 熔断 10 秒
DegradeRuleManager.loadRules(Collections.singletonList(rule));
```

## Dubbo Filter 集成

Sentinel 在 Dubbo Filter 链中工作：

```
Consumer 调用
    → Router → LoadBalance
    → SentinelDubboConsumerFilter（Consumer 端 Sentinel 检查）
    → 网络传输
    → SentinelDubboProviderFilter（Provider 端 Sentinel 检查）
    → 真实 Service 调用
```

Consumer 端和 Provider 端都可以配置规则，双重保护。""",
                "Sentinel,限流,熔断,集成,Dubbo Filter",
            ),
        ],
        [],
    ),
}


def seed_all(db):
    total_notes = total_interviews = 0
    for stack_name, (notes, interviews) in DATA.items():
        row = db.execute("SELECT id FROM stack WHERE name = ? AND group_name = 'Dubbo'", (stack_name,)).fetchone()
        if not row:
            print(f"  SKIP {stack_name}: not found")
            continue
        sid = row["id"]

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

    return total_notes, total_interviews


if __name__ == "__main__":
    db = get_db()
    n, i = seed_all(db)
    db.close()
    print(f"\nDubbo total: {n} notes + {i} interviews")
