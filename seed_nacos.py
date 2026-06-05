"""为 Nacos 技术栈填充知识笔记 + 常见面试题"""
from db import get_db

NOTES = [
    (
        "Nacos 的历史背景与演进",
        """## 诞生背景

在微服务架构大规模普及的 2017-2018 年，业界面临几个痛点：

1. **服务发现各自为战**：Netflix Eureka 进入维护模式，Consul 在服务发现上表现优秀但配置管理薄弱，ZooKeeper 强一致性在服务发现场景过度设计导致可用性问题。

2. **配置管理割裂**：Spring Cloud Config 需要外部 Git 仓库，Apollo 功能强大但运维成本高，Diamond 作为阿里内部方案已停止开源维护。

3. **"两套系统"的运维负担**：大部分团队需要同时维护一个注册中心（Eureka/Consul/ZK）+ 一个配置中心（Config/Apollo），两套集群、两套 SDK、两套控制台。

## Nacos 的诞生

Nacos（NAming and COnfiguration Service）由阿里巴巴在 **2018 年 7 月** 正式开源，目标是用一个平台统一解决 **服务发现 + 配置管理**。它的前身是阿里的内部组件：

| 内部组件 | 对应功能 |
|---------|---------|
| **VIPServer**（软负载）| Nacos 服务注册与发现 |
| **Diamond**（配置管理）| Nacos 配置中心 |
| **ACM**（Application Configuration Management）| Nacos 云上配置管理能力 |

## 关键里程碑

- **2018.07**: v0.1.0 开源，支持基本的服务发现和配置管理
- **2019.04**: v1.0.0 GA 发布，生产可用
- **2019.07**: 进入 CNCF Landscape
- **2020.12**: v2.0.0 发布，升级通信协议，性能大幅提升（长连接 gRPC 替代 HTTP 短轮询）
- **2022+**: 成为 Spring Cloud Alibaba 生态的核心组件""",
        "历史,演进,背景,起源,生态",
    ),
    (
        "Nacos 整体架构设计",
        """## Nacos 架构分层

```
┌─────────────────────────────────────────┐
│            接入层 (OpenAPI/SDK)          │
│   Java SDK / Go SDK / DNS-F / HTTP API  │
├─────────────────────────────────────────┤
│              核心功能层                   │
│  ┌──────────────┐  ┌──────────────┐     │
│  │  服务发现      │  │  配置管理      │     │
│  │  (Naming)    │  │  (Config)    │     │
│  └──────┬───────┘  └──────┬───────┘     │
│         │                 │              │
│  ┌──────┴─────────────────┴───────┐     │
│  │         一致性协议层              │     │
│  │  Distro (AP)  │  Raft (CP)     │     │
│  └───────────────┴─────────────────┘     │
├─────────────────────────────────────────┤
│              数据存储层                   │
│  内嵌 Derby / MySQL (集群模式)           │
└─────────────────────────────────────────┘
```

## 核心概念

| 概念 | 说明 |
|------|------|
| **Namespace** | 命名空间，用于租户隔离。默认 `public`，不同环境用不同 namespace（dev/test/prod）|
| **Group** | 服务/配置分组，同一 namespace 下的二级隔离 |
| **Service** | 服务名，一组提供相同功能的实例集合 |
| **Instance** | 实例，一个具体的服务节点（IP+Port）|
| **Cluster** | 虚拟集群，同一服务下可按机房/地域划分 |

## 设计原则

1. **数据与服务分离**：服务数据（注册信息）和配置数据分开存储和同步
2. **事件驱动**：服务变更通过事件通知下游，保证实时性
3. **自保护机制**：网络分区时优先保证可用性，防止集群雪崩""",
        "架构,设计,分层,概念",
    ),
    (
        "服务注册发现的完整流程",
        """## 服务注册

```
Provider                  Nacos Server              Consumer
   │                          │                         │
   │──① 注册请求──────────────→│                         │
   │   (serviceName, ip, port, │                         │
   │    metadata, weight...)   │                         │
   │                          │──② 存储实例信息           │
   │                          │──③ 推送变更事件─────────→│
   │                          │                         │──④ 更新本地缓存
   │←──⑤ 返回成功──────────────│                         │
```

1. Provider 启动后向 Nacos Server 发送注册请求
2. Server 将实例信息写入存储
3. Server 通过事件机制通知所有订阅了该服务的 Consumer
4. Consumer 收到事件后更新本地服务缓存列表

## 心跳机制（临时实例）

- Provider 每 **5 秒** 发送一次心跳
- Server 超过 **15 秒** 未收到心跳，标记实例为不健康
- Server 超过 **30 秒** 未收到心跳，剔除该实例

## 服务发现（拉取+推送）

1. Client 启动时**全量拉取**一次服务实例列表
2. Client 构建本地缓存（避免每次调用都查 Server）
3. **Server 主动推送**变更事件（gRPC 长连接）
4. Client 收到推送后增量更新本地缓存""",
        "注册,发现,心跳,流程",
    ),
    (
        "临时实例 vs 持久实例 —— 核心机制",
        """## 两种实例类型的本质区别

| 特性 | 临时实例（默认）| 持久实例 |
|------|-----------------|---------|
| **注册方式** | Agent（SDK）自动注册 | 人工或 Agent 注册 |
| **健康检查** | 客户端心跳上报 | Server 主动探测 |
| **剔除机制** | 心跳超时自动剔除 | 不健康不下线，需手动处理 |
| **数据一致性** | AP（Distro 协议）| CP（Raft 协议）|
| **适用场景** | 微服务（动态服务）| 基础设施（数据库/DNS/K8s Service）|

## 选择策略

> **默认使用临时实例。** Spring Cloud 项目中引入 starter 自动注册的服务默认就是临时实例。
>
> 当你有 MySQL / Redis / Elasticsearch 等基础设施需要注册到 Nacos 时，使用持久实例 + 手动健康检查端点。""",
        "临时实例,持久实例,ephemeral,心跳,AP,CP",
    ),
    (
        "Nacos 的 CAP 模式与一致性协议",
        """## Nacos 同时支持 AP 和 CP

Nacos 最大的创新之一是**在同一个集群中同时运行 AP 和 CP 两种一致性协议**。

## Distro 协议（AP 模式）

阿里自研的 **最终一致性** 协议，用于**临时实例的服务发现**：

1. **写流程**：写入任意一个 Server 节点即返回成功，异步同步到其他节点
2. **读流程**：每个节点维护全量数据副本，本地读取无需走 Raft 日志
3. **冲突解决**：采用 Last-Write-Wins 策略，以时间戳为准

## Raft 协议（CP 模式）

用于**持久实例和配置管理**，保证强一致性：

1. **写流程**：写入必须经过 Leader，Leader 将日志复制到过半 Follower 后 commit
2. **Leader 选举**：基于 Term 的逻辑时钟
3. **配置不回滚**：每次变更都是一条 Raft 日志，可追溯历史版本

> **本质**: Nacos 在 CAP 理论中没有固定选边——它在不同的数据上选择了不同的一致性策略。""",
        "CAP,一致性,Distro,Raft,协议,AP,CP",
    ),
    (
        "Nacos 配置中心机制详解",
        """## 配置存储模型

```
Namespace → Group → Data ID → Content + MD5
```

- **Data ID** 命名惯例：`${spring.application.name}-${profile}.${file-extension}`
- **MD5**：Client 对比本地缓存的 MD5 判断是否需要拉新配置

## 配置侦听机制

### gRPC 长连接（v2.x）

```
Client ←── gRPC Stream ──→ Server (双向流，复用一条 TCP 连接)
```

### 本地缓存兜底

当 Nacos Server 完全不可用时，Client 从本地快照文件读取配置，保证服务可以启动。

## 动态刷新

| 方式 | 原理 |
|------|------|
| **@RefreshScope** | Spring Cloud 的 RefreshScope Bean，重建代理对象 |
| **@NacosValue** | Nacos 原生注解，属性粒度自动刷新 |""",
        "配置中心,配置管理,长轮询,gRPC,动态刷新",
    ),
    (
        "Nacos 集群部署与生产最佳实践",
        """## 集群架构

```
   Nginx/ALB (VIP)
       │
  ┌────┼────┐
  │    │    │
Nacos Nacos Nacos  (3节点 Raft)
  │    │    │
  └────┼────┘
       │
    MySQL (外部存储)
```

## 部署要点

| 项目 | 建议 |
|------|------|
| 节点数 | 最少 3 节点 |
| 存储 | 集群模式必须用外部 MySQL |
| 端口 | 8848(HTTP) / 9848(gRPC Client) / 9849(gRPC Server) / 7848(Raft) |
| JVM | 堆内存 ≥ 2G |

## 生产 Checklist

- [ ] MySQL 8.0+ 外部存储，配置主从
- [ ] 至少 3 个 Nacos 节点
- [ ] 前面挂 Nginx/ALB 暴露 VIP
- [ ] 不同环境用不同 Namespace 隔离
- [ ] 开启权限认证
- [ ] 定期备份 MySQL 中的 config_info 表""",
        "集群,部署,生产,最佳实践,高可用",
    ),
    (
        "Nacos vs Eureka / Consul / ZK 对比",
        """## 注册中心对比

| 维度 | Nacos | Eureka | Consul | ZooKeeper |
|------|-------|--------|--------|-----------|
| **CAP 模型** | AP + CP 可切换 | AP | CP | CP |
| **一致性协议** | Distro / Raft | Peer to Peer | Raft | ZAB |
| **配置中心** | ✅ 内置 | ❌ | ✅ KV 存储 | ❌ |
| **控制台** | ✅ 完善 | ✅ 基础 | ✅ 完善 | ❌ 需第三方 |
| **雪崩保护** | ✅ | ✅ 自我保护 | ❌ | ❌ |
| **维护状态** | 活跃 | 维护模式 | 活跃 | 活跃 |
| **学习成本** | 中 | 低 | 中 | 高 |

## Eureka 为什么被淘汰？

1. **只能 AP**：网络分区时不能保证数据一致
2. **没有配置管理**：需额外部署 Config
3. **自我保护太激进**：网络波动时保留已下线实例导致调用到僵尸节点
4. **2.0 跳票**：Netflix 宣布后无实质进展""",
        "对比,Eureka,Consul,ZooKeeper,选型",
    ),
]

INTERVIEWS = [
    (
        "Nacos 的 CAP 模式是如何实现的？为什么能同时支持 AP 和 CP？",
        """## 参考答案

**Nacos 并没有在同一个数据上同时满足 AP 和 CP，而是对不同类型的数据采用不同的一致性协议。**

### 实现方式

Nacos 内置了两套一致性协议：

**Distro 协议（AP 模式）—— 用于临时实例的服务发现**

Distro 是阿里自研的最终一致性协议，核心特征：
- **写**：任意节点写入即成功，异步复制给其他节点
- **读**：每个节点本地都有全量数据，直接读本地
- **冲突解决**：Last-Write-Wins（以时间戳为准）
- **网络分区时**：每个分区独立提供服务，恢复后自动合并

选择 AP 的原因：服务发现场景下，**宁可看到过期的实例列表，也不能因为分区导致服务调用失败**。

**Raft 协议（CP 模式）—— 用于持久实例和配置管理**

Raft 是经典的强一致性协议：
- **写**：必须 Leader 处理，复制到过半节点才 commit
- **读**：通过 Leader 租约保证线性一致性
- **网络分区时**：少数派分区无法写入

选择 CP 的原因：**配置错误的代价远大于短暂不可用**（比如数据库连接串配错，可能直接导致生产事故）。

### 面试加分点

Nacos 的这种设计实际上回答了 CAP 理论的一个关键问题：**在实际系统中，不需要在全局选边，可以按数据粒度做不同取舍。** 同类的设计思路在 TiDB（MVCC + Raft，不同 key range 不同 Leader）、Kafka（不同 Topic 可以配置不同的一致性级别）中也有体现。

### 追问：Distro 协议和 Gossip 协议有什么区别？

- **Gossip**（Consul 使用）：随机选择邻居传播，所有节点对等，收敛慢但无中心
- **Distro**（Nacos 使用）：有中心的异步复制，单一节点写→全量同步，收敛快""",
        "CAP,Distro,Raft,一致性,高频",
    ),
    (
        "Nacos 和 Eureka 的区别是什么？为什么现在都用 Nacos？",
        """## 参考答案

### 核心区别

| 维度 | Nacos | Eureka |
|------|-------|--------|
| **功能范围** | 注册中心 + 配置中心 | 仅注册中心 |
| **CAP 模型** | AP + CP 可切换 | 纯 AP |
| **一致性协议** | Distro / Raft | Peer-to-Peer 复制 |
| **健康检查** | 心跳 + Server 主动探测 | 仅心跳 |
| **实例类型** | 临时 + 持久两种 | 只有一种 |
| **配置管理** | ✅ 内置 | ❌ 需要 Spring Cloud Config |
| **控制台功能** | 完善（服务列表、详情、元数据编辑）| 基础（查看注册信息）|
| **动态配置刷新** | ✅ 支持 | ❌ |
| **权限控制** | ✅ | ❌ |
| **维护状态** | 活跃开发 | 维护模式（只修 bug）|

### Eureka 被淘汰的根本原因

**1. 自我保护模式是双刃剑**

Eureka 的自我保护机制在网络波动时会保留所有实例——包括已下线的。这导致 Consumer 仍会路由到不存在的节点，造成调用失败。Nacos 用临时实例自动剔除 + 持久实例不下线的设计，更精确地区分了"网络抖动"和"实例真正挂了"。

**2. Netflix 放弃维护**

2018 年 Netflix 宣布 Eureka 2.0 开源计划后跳票，社区信心崩塌。而同期 Nacos 从阿里内部验证后正式开源，背靠 Spring Cloud Alibaba 生态迅速占领市场。

**3. 运维负担**

用 Eureka 必须再搭一套配置中心（Config/Apollo），两套集群、两套 SDK、两个控制台——运维成本翻倍。Nacos 一站式解决，省去大量工作。

### 面试加分点

可以提到在项目中**灰度迁移 Eureka → Nacos** 的经验：利用 Nacos 的 `spring.cloud.nacos.discovery.register-enabled=false` 配置，先在 Consumer 侧双注册、双订阅，验证无误后再切断 Eureka 流量。""",
        "对比,Eureka,区别,选型,高频",
    ),
    (
        "Nacos 服务注册的流程是怎样的？心跳机制如何工作？",
        """## 参考答案

### 服务注册流程

```
1. Provider 启动
2. 读取 spring.cloud.nacos.discovery.server-addr 配置
3. 构建 Instance 对象（serviceName, ip, port, metadata, weight, cluster...）
4. 调用 Nacos NamingService.registerInstance()
5. Nacos Server 收到请求：
   - 写入内存注册表（ConcurrentHashMap）
   - 如果是临时实例 → Distro 协议异步同步给其他节点
   - 如果是持久实例 → Raft 协议同步
6. Server 发布 ServiceChangedEvent
7. 所有订阅该服务的 Consumer 收到 push 通知
8. Provider 启动定时心跳任务
```

### 心跳机制（临时实例）

- **心跳间隔**：默认 5 秒（可配 `spring.cloud.nacos.discovery.heart-beat-interval`）
- **不健康阈值**：15 秒未收到心跳（3 个心跳周期）
- **剔除阈值**：30 秒未收到心跳（6 个心跳周期）
- **实现方式**（v2.x）：gRPC 长连接，复用同一条 TCP 连接发送心跳，比 v1.x 的 HTTP 心跳效率大幅提升

### 健康检查源码流程（简述）

```
Nacos Client 侧：
  BeatReactor.addBeatInfo()
    → 创建定时任务，每 5s 通过 gRPC 发送 BeatInfo
    → Server 返回下一次心跳间隔（可动态调整）

Nacos Server 侧：
  ClientBeatProcessor 处理心跳
    → 更新实例的 lastBeatTime
    → 如果是持久实例则走 Raft（注意：持久实例走 HealthCheck 而非心跳）

HealthCheckTask（Server 定时任务）：
  → 遍历所有实例
  → lastBeatTime + 15s < now → 标记 UNHEALTHY
  → lastBeatTime + 30s < now → 删除实例
```

### 面试加分点

可以提到 v1.x（HTTP 短连接）→ v2.x（gRPC 长连接）的升级带来的性能变化：**单节点连接的客户端数量从千级提升到万级**，因为 gRPC 多路复用一条 TCP 连接承载服务发现心跳 + 配置监听。""",
        "注册流程,心跳,源码,流程",
    ),
    (
        "Nacos 配置中心是如何实现动态刷新的？",
        """## 参考答案

### 刷新机制全链路

```
1. 用户在控制台修改配置 → Nacos Server 写入 MySQL + 发布 ConfigDataChangeEvent

2. Server 端：长轮询 or gRPC 双向流
   v1.x: HTTP 长轮询（Long Polling）
     - Client 发起请求，Header 带 Long-Pulling-Timeout=30000ms
     - 30s 内配置变化 → 立即返回新配置 MD5
     - 30s 无变化 → 返回 304 Not Modified
     - Client 收到响应后立即发起下一次长轮询

   v2.x: gRPC Stream（推荐）
     - Client 一次注册监听
     - Server 有变化时主动推送 ConfigChangeNotifyRequest
     - 不再需要轮询，实时性更好

3. Client 端：收到变更通知后
   - 对比本地缓存的 MD5
   - MD5 不一致 → 主动拉取最新配置内容
   - 保存到本地 snapshot 文件（兜底用）
   - 触发 Spring Cloud 的 RefreshEvent

4. Spring 容器：
   - @RefreshScope 标注的 Bean → ContextRefresher 销毁旧 Bean
   - 下次请求时重新创建 Bean，新配置生效
   - @NacosValue(autoRefreshed=true) → 属性级别直接更新
```

### 关键细节

**为什么需要本地快照？**
- Server 完全挂掉时，Client 从 `~/nacos/snapshot/` 读取上次缓存的配置
- 保证服务可以启动——只是用旧配置

**长轮询 vs gRPC 的区别：**
- 长轮询：Client 每次收到响应（无论有无变化）都要立即发起新的请求
- gRPC：一次连接，Server 随时推送，无请求开销

### 面试加分点

**刷新是 Bean 级别，不是属性级别。** `@RefreshScope` 的作用是标记一个 Bean 为"可刷新"，刷新时销毁旧的 Bean 实例，下次请求时创建新的——新的 Bean 自然就读取了新配置。所以：
- 单例 Bean 用 `@RefreshScope` 不再是单例
- 如果 Bean 持有连接池等资源，刷新时记得在 `@PreDestroy` 中释放""",
        "配置中心,动态刷新,RefreshScope,长轮询,高频",
    ),
    (
        "Nacos 集群部署时需要考虑哪些问题？如何保证高可用？",
        """## 参考答案

### 集群部署关键点

**1. 节点数量与 CAP 权衡**

最少 3 节点（Raft 需要 2n+1 法定人数）。生产建议 3~5 节点：
- 3 节点：容忍 1 台故障
- 5 节点：容忍 2 台故障

**2. 外部存储**

集群模式**必须使用 MySQL**，内嵌 Derby 仅限单机开发。所有 Nacos 节点共享同一个 MySQL（建议 MySQL 自身做主从或 MGR）。

**3. 端口规划**

| 端口 | 偏移公式 | 用途 |
|------|---------|------|
| 8848 | 主端口 | HTTP API + 控制台 |
| 9848 | 8848+1000 | gRPC Client 通信（SDK → Server）|
| 9849 | 8848+1001 | gRPC Server 通信（集群内部）|
| 7848 | 8848-1000 | Raft 协议通信 |

**4. 负载均衡**

Nacos 集群前面必须挂 Nginx/ALB/SLB，Client SDK 只配置 VIP 地址：

```nginx
upstream nacos_cluster {
    server 192.168.1.10:8848;
    server 192.168.1.11:8848;
    server 192.168.1.12:8848;
}
```

### 高可用保障

- **MySQL 高可用**：主从 + 故障自动切换（MHA/Orchestrator）
- **Nacos 自身高可用**：Raft 自动选举，Leader 宕机后秒级选出新 Leader
- **Client 侧容灾**：本地缓存 + snapshot 文件兜底
- **多机房**：可按 Cluster 划分，同机房优先调用

### 面试加分点

**Nacos 集群的分区容错能力**：对于临时实例（Distro AP），网络分区后每个分区都能独立注册和发现——代价是分区恢复后需要合并冲突数据（Last-Write-Wins）。对于配置和持久实例（Raft CP），只有多数派分区可以工作。""",
        "集群,高可用,部署,架构",
    ),
    (
        "Nacos 2.x 相比 1.x 有哪些重大改进？",
        """## 参考答案

### 核心变化：通信协议升级

| 维度 | 1.x | 2.x |
|------|-----|-----|
| **通信协议** | HTTP（短连接为主）| gRPC（长连接）|
| **心跳** | HTTP 请求，每次建连 | gRPC Stream，复用连接 |
| **配置监听** | HTTP 长轮询 | gRPC 双向流推送 |
| **单节点连接数** | 千级别 | 万级别 |
| **CPU 消耗** | 高（频繁建连/拆连）| 低（连接复用）|
| **网络开销** | 大（HTTP Header 每次重复）| 小（二进制 Protobuf）|

### 具体改进

**1. 长连接取代短连接**

v1.x 每个心跳都是一次 HTTP POST，对于万级实例的集群，Server 端需要处理每秒数千次 HTTP 请求——CPU 大部分消耗在 TLS 握手和 HTTP 解析上。v2.x 的 gRPC 长连接复用一条 TCP，心跳只是 Stream 上的一条 Protobuf 消息。

**2. 配置推送实时性提升**

v1.x 的 HTTP 长轮询，Client 收到 304 后发起下一次轮询存在毫秒级间隙。v2.x 的 gRPC 双向流 Server 可以随时 push，真正做到实时。

**3. 插件化健康检查**

v2.x 将健康检查抽象为 SPI 插件，不再只能用 TCP/HTTP/MySQL，可以自定义。

### 面试加分点

迁移时的一个实践：gRPC 端口 9848 是 8848+1000，**防火墙别忘了开 gRPC 端口**——这是 1.x → 2.x 升级最常见的踩坑点。Client 1.x 访问 8848 即可，2.x SDK 会同时使用 8848 + 9848。""",
        "2.x,1.x,版本,改进,gRPC,升级",
    ),
]


def seed():
    db = get_db()
    nacos = db.execute("SELECT id FROM stack WHERE name LIKE '%Nacos%'").fetchone()
    if not nacos:
        print("Nacos stack not found!")
        return
    stack_id = nacos["id"]

    # 清除旧条目
    db.execute("DELETE FROM entry WHERE stack_id = ?", (stack_id,))

    for title, content, tags in NOTES:
        db.execute(
            "INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?, ?, ?, ?, 'note')",
            (stack_id, title, content, tags),
        )

    for title, content, tags in INTERVIEWS:
        db.execute(
            "INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?, ?, ?, ?, 'interview')",
            (stack_id, title, content, tags),
        )

    db.commit()
    db.close()
    print(f"Nacos: {len(NOTES)} notes + {len(INTERVIEWS)} interview questions inserted")


if __name__ == "__main__":
    seed()
