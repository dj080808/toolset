"""中间件技术栈组：微服务常用中间件"""
from db import get_db

STACKS = [
    # P0: 前置基础
    ("Netty", "高性能网络通信框架，Java NIO 的事实标准，大量中间件底层依赖", 0, 0),
    # P1: 消息中间件
    ("RabbitMQ", "AMQP 协议实现，Erlang 编写，可靠消息投递、死信队列、延迟队列", 1, 0),
    ("Kafka", "分布式流平台，LinkedIn 开源，万亿级消息处理，日志收集和流计算首选", 2, 0),
    ("RocketMQ", "阿里开源，Java 编写，事务消息、顺序消息，双11验证的金融级可靠性", 3, 0),
    # P2: 缓存与NoSQL
    ("Redis", "内存数据结构存储，缓存/分布式锁/消息队列/布隆过滤器，微服务基础设施之王", 4, 0),
    ("Elasticsearch", "分布式搜索引擎，Lucene 内核，全文检索、日志分析（ELK）、APM", 5, 0),
    ("MongoDB", "文档型 NoSQL 数据库，JSON 存储，适合日志、社交、物联网等非结构化数据", 6, 0),
    # P3: 数据库与数据同步
    ("MySQL", "关系型数据库，InnoDB 引擎，事务/MVCC/索引优化/主从复制/分库分表", 7, 0),
    ("ShardingSphere", "Apache 分库分表中间件，Sharding-JDBC/Sharding-Proxy 两种模式", 8, 0),
    ("Canal", "阿里开源 MySQL binlog 订阅组件，数据同步/缓存更新/实时数仓的利器", 9, 0),
    # P4: 分布式协调与调度
    ("ZooKeeper", "分布式协调服务，CP 模型，分布式锁/选主/配置管理/服务发现", 10, 0),
    ("XXL-Job", "大众点评开源分布式任务调度平台，Cron/分片/失败重试/可视化", 11, 0),
    # P5: 运维与基础设施
    ("Nginx", "高性能 HTTP/反向代理服务器，负载均衡/静态资源/SSL 卸载/限流", 12, 0),
    ("Docker", "容器化引擎，镜像/容器/仓库，微服务部署标准，docker-compose/k8s 基石", 13, 0),
    ("Prometheus + Grafana", "CNCF 监控标准，Prometheus 采集 + Grafana 展示，生产监控标配", 14, 0),
    ("ELK (Elasticsearch + Logstash + Kibana)", "日志收集分析平台，Filebeat 采集 → Logstash 处理 → ES 存储 → Kibana 展示", 15, 0),
    ("Jenkins", "CI/CD 持续集成工具，Pipeline as Code，自动化构建/测试/部署", 16, 0),
    ("MinIO", "高性能对象存储，S3 兼容 API，私有化部署替代 OSS/S3 的首选", 17, 0),
]

NOTES = {
    "Netty": [(
        "Netty 的历史与核心原理",
        """## 起源

Netty 由 **Trustin Lee**（韩国）在 2004 年创建，最初是 JBoss 的一个子项目。2008 年发布 3.x，2013 年发布 4.x（现在的主力版本）。

Netty 解决的问题：Java 原生的 NIO API（`java.nio`）太难用了。ByteBuffer 的 flip/clear、Selector 的事件处理、粘包拆包……开发者要写大量样板代码。

Netty 做了封装：**一个 EventLoop 对应一个线程 + 一个 Selector**，让 NIO 开发变得简单。

## 核心架构

```
BossGroup (1 个 EventLoop)
    │ accept 新连接
    ↓ 注册到 WorkerGroup
WorkerGroup (N 个 EventLoop = CPU 核数 × 2)
    │ 每个 EventLoop 绑定多个 Channel
    ├→ ChannelPipeline（责任链）
    │   ├→ Encoder（编码）
    │   ├→ Decoder（解码）
    │   └→ ChannelHandler（业务处理）
    └→ 一个线程处理多个连接的 IO 事件
```

## Reactor 模型

| 模型 | Boss 线程 | Worker 线程 |
|------|----------|------------|
| 单 Reactor（NIO 基础）| 1 | 0（Boss 兼做 Worker）|
| 多 Reactor（Netty 默认）| 1 | CPU × 2 |
| 主从多 Reactor | N | CPU × 2 |

## 谁在用 Netty

- Dubbo、gRPC 的通信层
- RocketMQ 的网络通信
- Elasticsearch 的节点间通信
- Zookeeper 3.5+ 的 Netty 版本
- Spring WebFlux 底层 Reactor Netty

> 面试金句：Netty 是 Java 网络编程的"终结者"。几乎所有高性能 Java 中间件的底层通信都依赖它。""",
        "历史,Reactor,NIO,EventLoop,架构",
    )],
    "RabbitMQ": [(
        "RabbitMQ 的历史与核心原理",
        """## 起源

RabbitMQ 2007 年由 Rabbit Technologies 发布，基于 **AMQP（Advanced Message Queuing Protocol）0-9-1** 协议。2010 年被 VMware 收购，后并入 Pivotal。

用 Erlang 编写（Erlang 天生适合并发和容错），所以 RabbitMQ 的**集群和高可用能力非常强**。

## 核心概念

```
Producer → Exchange → (Binding 路由规则) → Queue → Consumer
                ↓
        四种 Exchange 类型：
        ├── Direct:    精确匹配 routing key
        ├── Topic:     通配符匹配 routing key（# 多级, * 单级）
        ├── Fanout:    广播到所有绑定的 Queue
        └── Headers:   按 Header 匹配（极少用）
```

## 高级特性

| 特性 | 原理 | 场景 |
|------|------|------|
| **消息确认（ACK）** | Consumer 处理完手动 ACK | 保证消息不丢失 |
| **死信队列（DLX）** | 超时/被拒绝/NACK 的消息进入 DLX | 异常消息兜底 |
| **延迟队列** | TTL + DLX 组合，或 rabbitmq_delayed_message_exchange 插件 | 订单超时取消 |
| **镜像队列** | 队列数据同步到多个节点 | 高可用 |
| **持久化** | 消息和队列都持久化到磁盘 | 重启不丢消息 |

## 和 Kafka 的区别

| 维度 | RabbitMQ | Kafka |
|------|----------|-------|
| 设计目标 | 消息可靠投递 | 高吞吐流处理 |
| 吞吐量 | 万级/秒 | 百万级/秒 |
| 消息回溯 | ❌（消费完删除）| ✅（按 offset 回溯）|
| 协议 | AMQP 标准 | 自定义协议 |
| 适用场景 | 业务消息、RPC、延迟消息 | 日志、流计算、事件溯源 |""",
        "架构,Exchange,Queue,AMQP,原理",
    )],
    "Kafka": [(
        "Kafka 的历史与核心原理",
        """## 起源

Kafka 2011 年由 **LinkedIn** 开源，由 Jay Kreps（后来创办 Confluent）创建。设计目标是解决 LinkedIn 每天万亿级消息的实时数据管道问题。名字来源于作家 Franz Kafka（意为"为写作而生的系统"）。

## 核心概念

| 概念 | 说明 |
|------|------|
| **Topic** | 消息分类（类似数据库的表）|
| **Partition** | Topic 的分区，每个 Partition 是一个有序的不可变日志 |
| **Producer** | 生产者，向 Topic 的某个 Partition 写数据 |
| **Consumer** | 消费者，从 Partition 按 offset 顺序读数据 |
| **Consumer Group** | 消费者组，组内每个 Consumer 负责不同的 Partition |
| **Broker** | Kafka 服务器节点 |
| **ZooKeeper / KRaft** | 元数据管理（3.3+ 用 KRaft 替代 ZK）|

## Partition 机制（核心）

```
Topic: user-events
├── Partition 0: [msg0, msg1, msg2, msg3, ...]  ← 消息按 offset 有序
├── Partition 1: [msg0, msg1, msg2, ...]
└── Partition 2: [msg0, msg1, msg2, ...]

Consumer Group A:
  Consumer1 → Partition 0 + Partition 1
  Consumer2 → Partition 2

Consumer Group B:
  Consumer3 → Partition 0 + Partition 1 + Partition 2
  (多 Consumer Group 独立消费，互不影响)
```

## 为什么吞吐量高

1. **顺序写磁盘**：Partition 日志按顺序追加，类比写日志文件，比随机写快几个数量级
2. **零拷贝（sendfile）**：数据从磁盘 → Page Cache → 网卡，不经过用户态
3. **批量处理**：Producer/Consumer 都支持 batch，减少网络和 IO 开销
4. **Page Cache**：大量依赖 OS 的页缓存而非 JVM 堆内存

## ISR 机制

```
Partition 0:
  Leader   (Broker 1)：负责读写
  Follower (Broker 2)：同步正常 → 在 ISR 列表中
  Follower (Broker 3)：同步滞后 → 从 ISR 列表中移除

ISR = In-Sync Replicas = 和 Leader 保持同步的副本集合
只有当消息被所有 ISR 确认后，才算 commit
```""",
        "Partition,ISR,吞吐量,offset,零拷贝",
    )],
    "RocketMQ": [(
        "RocketMQ 的历史与核心原理",
        """## 起源

RocketMQ 2012 年由**阿里巴巴**开源，最初叫 MetaQ，后改名 RocketMQ，2017 年进入 Apache 成为顶级项目。

阿里内部经历了从 ActiveMQ → Kafka（深度魔改版，MetaQ 1.0/2.0）→ RocketMQ（重写，MetaQ 3.0）的演进。

## 核心概念

| 概念 | 对应 Kafka | 说明 |
|------|-----------|------|
| Topic | Topic | 消息主题 |
| Message Queue | Partition | 消息队列（最小存储单元）|
| Producer Group | - | 生产者组（事务消息需要）|
| Consumer Group | Consumer Group | 消费者组 |
| NameServer | ZK/KRaft | 路由注册中心（无状态）|
| Broker | Broker | 消息存储服务器 |

## 和 Kafka 的核心区别

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 存储 | Partition 日志 | CommitLog + ConsumeQueue |
| 注册中心 | ZK / KRaft | NameServer（自研，更轻量）|
| 事务消息 | ❌ 无原生支持 | ✅ 事务消息（半消息机制）|
| 顺序消息 | Partition 内有序 | ✅ Queue 内严格有序 |
| 延迟消息 | ❌ 需自行实现 | ✅ 18 个延迟级别内置 |
| 消息过滤 | ❌ | ✅ Tag + SQL 过滤 |
| 适用场景 | 流处理、日志 | 业务消息（订单、支付）|

## 事务消息（RocketMQ 独有）

```
① Producer 发送半消息（Half Message，Consumer 看不到）
② 执行本地事务
③ 本地事务成功 → Commit → Consumer 可见
   本地事务失败 → Rollback → 消息删除
④ 如果 Producer 宕机，Broker 定时回查本地事务状态
```

## CommitLog + ConsumeQueue 存储模型

```
CommitLog（所有 Topic 的消息顺序写入同一个文件）
    │  每条消息都有物理 offset
    │
    ├→ ConsumeQueue（TopicA-Queue0）：按顺序存消息的 offset
    ├→ ConsumeQueue（TopicA-Queue1）
    └→ ConsumeQueue（TopicB-Queue0）
        每个 ConsumeQueue 只存 20 字节/条（offset + size + tag hash）
        顺序读 ConsumeQueue → 随机读 CommitLog（Page Cache 命中率高）
```

> 选型：业务消息（订单/支付）→ RocketMQ（事务消息、延迟消息）；日志/流处理 → Kafka（吞吐优先）""",
        "事务消息,CommitLog,ConsumeQueue,NameServer,对比",
    )],
    "Redis": [(
        "Redis 的历史与核心原理",
        """## 起源

Redis（Remote Dictionary Server）由 **Salvatore Sanfilippo**（意大利，网名 antirez）在 2009 年创建。最初是为了解决他的网站实时统计的性能问题。

Redis 是**单线程事件驱动**模型（6.0+ 引入多线程 IO，但命令执行仍是单线程），所有操作原子化。

## 五种核心数据结构

| 类型 | 实现 | 用途 |
|------|------|------|
| **String** | SDS（简单动态字符串）| 缓存、计数器、分布式锁 |
| **List** | QuickList（3.2+）| 消息队列、最新列表 |
| **Set** | Dict / IntSet | 标签、共同好友 |
| **Sorted Set** | SkipList + Dict | 排行榜、延迟队列 |
| **Hash** | Dict / ZipList | 对象存储、购物车 |

## 高级数据结构

| Redis 5.0+ |
|-------------|
| **Stream**：持久化消息队列，支持 Consumer Group |
| **HyperLogLog**：基数统计，误差 0.81%，12KB 可统计 2^64 |
| **Geo**：地理位置计算（附近的人）|
| **Bitmap**：位图（签到统计）|
| **BloomFilter**（RedisBloom 模块）：去重判断 |

## 缓存三大问题

| 问题 | 现象 | 解决方案 |
|------|------|---------|
| **穿透** | 查不存在的数据 → 每次都打 DB | 布隆过滤器 / 空值缓存 |
| **击穿** | 热点 key 过期 → 大量请求打 DB | 互斥锁 / 永不过期 + 异步更新 |
| **雪崩** | 大量 key 同时过期 → DB 崩溃 | 过期时间加随机值 / 多级缓存 |

## 持久化

| 方式 | 原理 | 特点 |
|------|------|------|
| **RDB** | 定时快照二进制 dump | 恢复快，可能丢数据 |
| **AOF** | 追加每条写命令 | 数据安全，文件大 |
| **混合**（4.0+）| RDB + 增量 AOF | 兼顾恢复速度和数据安全 |

> Redis 不只是缓存——分布式锁、消息队列、排行榜、去重、限流、Session 共享……"微服务基础设施之王"绝非虚名。""",
        "数据结构,缓存,持久化,穿透,击穿,雪崩",
    )],
    "Elasticsearch": [(
        "Elasticsearch 的历史与核心原理",
        """## 起源

Elasticsearch 2010 年由 **Shay Banon**（以色列）发布，基于 Apache Lucene 构建。名字表达"弹性搜索"。

## 核心概念

| ES 概念 | 类比 MySQL | 说明 |
|---------|-----------|------|
| Index | Database | 索引，一组 Document 的集合 |
| Type | （7.x 已废弃）| 曾经类比 Table，现在一个 Index 只有一个 Type=_doc |
| Document | Row | 文档，一条 JSON 记录 |
| Field | Column | 字段 |
| Mapping | Schema | 字段类型定义 |
| Shard | 分片 | Lucene 实例，数据水平拆分 |
| Replica | 副本 | Shard 的复制，高可用 + 分摊读 |

## 倒排索引（核心）

```
传统查询：遍历所有文档找关键词 → 慢
倒排索引：维护"词 → 文档列表"的映射 → 快

词项          文档列表
elastic      [doc1, doc3, doc5]
search       [doc2, doc3, doc4]
spring       [doc1, doc2, doc5]

查询 "elastic spring" → 取交集 [doc1, doc5] → 毫秒级返回
```

## 写入流程

```
Client → Node (协调节点)
           │
           ├→ 计算 document_id % shard_count → 确定写入哪个 Shard
           ├→ 写入 Primary Shard
           ├→ Primary Shard 同步到 Replica Shards
           └→ 返回成功

近实时（NRT）：默认 1 秒 refresh 一次
写入 → refresh → 可被搜索（不是写磁盘，而是写 Lucene IndexSegment）
写入 → translog → 刷磁盘（fsync，保证数据不丢）
```

## 分片策略

```
3 节点集群，Index 设置 3 Primary Shard + 1 Replica：

  Node 1: P0, R2    ← Primary Shard 0 + Replica Shard 2
  Node 2: P1, R0
  Node 3: P2, R1

每个 Shard 是一个独立的 Lucene 实例
Primary 负责写，Replica 分担读
```""",
        "倒排索引,分片,近实时,Lucene,ELK",
    )],
    "MongoDB": [(
        "MongoDB 的历史与核心原理",
        """## 起源

MongoDB 2009 年由 **10gen**（后改名 MongoDB Inc.）发布，名字来自 humongous（巨大）。

定位：**JSON 文档数据库**，填补关系型数据库和 KV 存储之间的空白。

## MongoDB vs MySQL

| 维度 | MySQL | MongoDB |
|------|-------|---------|
| 数据模型 | 表 + 行 | Collection + Document（BSON）|
| Schema | 严格 Schema | Schema-less（灵活）|
| 关联 | JOIN | 内嵌文档 / $lookup |
| 事务 | ACID（行级）| ACID（4.0+ 多文档）|
| 扩展 | 主从 + 分库分表 | 原生 Sharding |
| 适用场景 | 结构化数据、关联查询多 | 日志、IoT、社交动态、非结构化数据 |

## 复制集（Replica Set）

```
Primary   ← 读写都在这里
Secondary ← 异步复制，可分担读
Arbiter   ← 仅投票，不存数据（打破选举平票）

选举基于 Raft 协议
```

## 分片集群

```
Mongos（路由层）→ Config Server（元数据）→ Shard 1 / Shard 2 / Shard 3

Shard Key 选择至关重要：
- 好的 Shard Key：数据均匀分布，查询能定位到具体 Shard
- 差的 Shard Key：数据倾斜，某个 Shard 成为热点
```

> 选型：日志/爬虫数据/社交 Feed → MongoDB（Schema 灵活，嵌套文档）；财务/订单 → MySQL（ACID 事务，关联查询）""",
        "文档,BSON,复制集,分片,MongoDB对比",
    )],
    "MySQL": [(
        "MySQL 核心原理面试要点",
        """## InnoDB 存储引擎

| 特性 | 说明 |
|------|------|
| **B+Tree 索引** | 所有数据存在叶子节点，非叶子节点只存 key |
| **MVCC** | 多版本并发控制，ReadView + Undo Log，读不阻塞写 |
| **Redo Log** | 物理日志，崩溃恢复，保证持久性 |
| **Undo Log** | 逻辑日志，回滚 + MVCC 读取历史版本 |
| **Binlog** | 逻辑日志，主从复制 + 数据恢复 |
| **行锁** | Record Lock / Gap Lock / Next-Key Lock |
| **Buffer Pool** | 内存缓冲池，缓存数据页和索引页 |

## 索引优化要点

```sql
-- 最左前缀原则
INDEX idx_a_b_c (a, b, c)
WHERE a=1           -- ✅ 用到索引
WHERE a=1 AND b=2   -- ✅ 用到索引
WHERE b=2           -- ❌ 用不到索引（不满足最左前缀）
WHERE a=1 AND c=3   -- ⚠️ 只用到了 a 列（跳过了 b）

-- 覆盖索引
SELECT a, b FROM t WHERE a=1  -- ✅ 直接从索引取数据，不回表
SELECT * FROM t WHERE a=1     -- ❌ 需要回表查完整行
```

## 事务隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 |
|------|------|----------|------|
| READ UNCOMMITTED | ✅ | ✅ | ✅ |
| READ COMMITTED | ❌ | ✅ | ✅ |
| REPEATABLE READ（InnoDB 默认）| ❌ | ❌ | ❌（Next-Key Lock 解决）|
| SERIALIZABLE | ❌ | ❌ | ❌ |

> InnoDB 在 RR 级别下通过 Next-Key Lock 解决了幻读问题。""",
        "InnoDB,B+Tree,MVCC,索引,隔离级别",
    )],
    "ShardingSphere": [(
        "ShardingSphere 的历史与核心原理",
        """## 起源

ShardingSphere 2016 年由**当当网**开源（Sharding-JDBC），2018 年进入 Apache 孵化器，2020 年毕业成为顶级项目。

## 两种模式

| 模式 | 形态 | 优点 | 缺点 |
|------|------|------|------|
| **Sharding-JDBC** | jar 包，嵌入应用 | 性能高，无额外部署 | 仅 Java |
| **Sharding-Proxy** | 独立进程，MySQL 协议 | 跨语言，对应用透明 | 多一跳，有性能损耗 |

## 核心能力

```
ShardingSphere 不只是分库分表！
├── 数据分片：水平分库、水平分表、垂直分库
├── 读写分离：一主多从，写主读从
├── 数据加密：敏感字段自动加解密
├── 影子库：灰度/压测流量打到影子库
└── 分布式治理：配合 ZK/Nacos 做配置管理
```

## 分片策略

```yaml
# 按 user_id 取模分片
sharding:
  tables:
    t_order:
      actualDataNodes: ds${0..1}.t_order${0..1}  # 2库 × 2表 = 4个分片
      databaseStrategy:
        standard:
          shardingColumn: user_id
          algorithmExpression: ds${user_id % 2}
      tableStrategy:
        standard:
          shardingColumn: order_id
          algorithmExpression: t_order${order_id % 2}
```

## 分库分表的核心问题

1. **分布式 ID**：雪花算法，保证全局唯一
2. **跨分片查询**：尽量避免，按 user_id 分片则所有查询都带 user_id
3. **分布式事务**：Seata AT 模式集成
4. **数据迁移**：扩容时数据重分布""",
        "分库分表,Sharding-JDBC,分片策略,读写分离",
    )],
    "Canal": [(
        "Canal 的历史与核心原理",
        """## 起源

Canal 由**阿里巴巴**在 2013 年开源，名字意为"运河"（连接 MySQL 和其他系统的数据水道）。

## 工作原理

Canal 伪装成 MySQL Slave，消费 Master 的 binlog：

```
MySQL Master
    │ binlog dump（模拟 Slave 协议）
    ↓
Canal Server（解析 binlog → CanalEntry 事件）
    │
    ├→ Canal Client (Java) → 业务处理（缓存更新、索引同步）
    ├→ 投递到 Kafka / RocketMQ
    └→ Flink / Spark Streaming 消费做实时计算
```

## 典型场景

| 场景 | 说明 |
|------|------|
| **缓存一致性** | 监听商品表变更 → 更新 Redis 缓存 |
| **索引同步** | 监听订单表变更 → 同步到 Elasticsearch |
| **实时数仓** | binlog → Kafka → Flink → ClickHouse |
| **数据同步** | MySQL A 库 → Canal → MySQL B 库（异地多活）|
| **审计日志** | 记录所有数据变更，谁在什么时候改了啥 |

## Canal Adapter

Canal 1.1.5+ 提供了 Adapter 组件，内置 ES/HBase/Kudu 等写入适配器，配置即可用，不用写 Client 代码。

```yaml
# 配置 MySQL → ES 同步
canalAdapters:
  - instance: example
    groups:
      - groupId: g1
        outerAdapters:
          - name: es
            hosts: 127.0.0.1:9300
            properties:
              mode: transport
```

> 面试加分：Canal 只关心数据变更事件（INSERT/UPDATE/DELETE），不参与业务逻辑，对 MySQL 性能影响极小（伪装 Slave 消费 binlog 是异步的）。""",
        "binlog,CDC,数据同步,缓存一致性,MySQL",
    )],
    "ZooKeeper": [(
        "ZooKeeper 的历史与核心原理",
        """## 起源

ZooKeeper 源于 **Yahoo!** 在 2006 年的内部项目，2010 年捐给 Apache。名字意为"动物园管理员"（管理 Hadoop 生态的各种"动物"）。

## 数据模型

```
/                           ← 根节点
├── /dubbo                  ← 持久节点
│   └── /com.example.UserService
│       └── /providers
│           ├── /192.168.1.10:20880   ← 临时节点（Session 断开后自动删除）
│           └── /192.168.1.11:20880
├── /locks
│   └── /order-lock-001     ← 临时顺序节点（分布式锁）
└── /config
    └── /app-config          ← 持久节点（配置管理）
```

## Session 与 Watch

```
Client 创建 Session → Server 分配 SessionID
    │
    ├→ Client 注册 Watch
    │    "我要监视 /dubbo/xxx/providers 的子节点变化"
    │
    ├→ 子节点变化 → Server 触发一次性回调（Watch 用完即删）
    │    Client 收到通知 → 重新注册 Watch
    │
    └→ Client 心跳（ping）→ Server 维持 Session
        30s 无心跳 → Session 过期 → 临时节点被删除
```

## ZAB 协议（CP 模型）

ZAB（ZooKeeper Atomic Broadcast）是 ZK 的一致性协议：

```
Leader                     Follower
  │                           │
  ├→ ① 收到写请求              │
  ├→ ② 生成 ZXID（事务 ID）    │
  ├→ ③ 发送 Proposal ──────→  │
  │                           ├→ ④ 写入本地日志
  │   ←────── ACK ────────────│
  ├→ ⑤ 收到过半 ACK 后 Commit  │
  ├→ ⑥ 发送 Commit ────────→  │
  │                           └→ ⑦ 应用到内存
```

## 典型用途

| 用途 | 实现 | 注意 |
|------|------|------|
| **分布式锁** | 临时顺序节点 + Watch | Curator 封装好直接用 |
| **选主** | 最小临时顺序节点成为 Leader | 注意 Session 过期后重新选举 |
| **配置管理** | 持久节点 + Watch | 小量配置 OK，大量配置用 Nacos |
| **服务发现** | 临时节点 + Watch | Dubbo 默认方案，但 Nacos 更好 |

> ZK 不适合高频写入和大量数据存储。它是"协调器"不是"数据库"。""",
        "ZAB,Session,Watch,临时节点,CP",
    )],
    "XXL-Job": [(
        "XXL-Job 的历史与核心原理",
        """## 起源

XXL-Job 由**许雪里**（大众点评）在 2015 年开源，是当前国内最流行的分布式任务调度平台。名字意为"XXL 号大任务"。

## 架构

```
┌──────────────────┐
│  XXL-Job Admin    │  ← 调度中心（Web 控制台 + 调度器）
│  (管理 + 调度)     │
└────────┬─────────┘
         │ HTTP 通信
    ┌────┼────┐
    │    │    │
┌───┴─┐┌─┴───┐┌┴───┐
│执行器││执行器││执行器│  ← 执行器（你的 Spring Boot 应用）
│  A  ││  B  ││  C  │
└─────┘└─────┘└─────┘
```

## 核心特性

| 特性 | 说明 |
|------|------|
| **Cron 调度** | 标准 CRON 表达式 |
| **分片广播** | 一个任务广播给所有执行器，按分片参数各自处理 |
| **失败重试** | 任务失败后自动重试 |
| **失败告警** | 邮件通知 |
| **任务依赖** | DAG 图管理任务依赖 |
| **动态启停** | 控制台在线操作，无需重启 |
| **GLUE 模式** | 在线编辑任务代码（Groovy），热部署 |

## 分片广播示例

```java
@XxlJob("shardingJob")
public void shardingJob() {
    int shardIndex = XxlJobHelper.getShardIndex();  // 当前分片序号
    int shardTotal = XxlJobHelper.getShardTotal();  // 总分片数

    // 每个执行器处理自己的那一段数据
    // 执行器 0 处理 id % 3 == 0 的数据
    // 执行器 1 处理 id % 3 == 1 的数据
    // 执行器 2 处理 id % 3 == 2 的数据
    List<User> users = userService.getByShard(shardIndex, shardTotal);
    processBatch(users);
}
```

## vs Quartz / Elastic-Job

| 维度 | Quartz | XXL-Job | Elastic-Job |
|------|--------|---------|-------------|
| 架构 | 嵌入应用 | Admin+执行器（中心化）| ZK 协调（去中心化）|
| 可视化 | ❌ | ✅ Web 控制台 | ❌ |
| 分片 | ❌ | ✅ 分片广播 | ✅ |
| 动态操作 | ❌ | ✅ 在线启停 | ✅ |
| 学习成本 | 低 | 低 | 中 |""",
        "任务调度,分片,Cron,Admin,Quartz",
    )],
    "Nginx": [(
        "Nginx 的历史与核心原理",
        """## 起源

Nginx 由 **Igor Sysoev**（俄罗斯）在 2004 年发布，最初是为了解决 C10K 问题——如何在一台服务器上支撑 10000 个并发连接。

## 架构核心

Apache 是**一连接一线程/进程**，Nginx 是**异步非阻塞事件驱动**：

```
Master Process（管理）
    ├── Worker 1（单线程 Event Loop）
    ├── Worker 2（单线程 Event Loop）
    ├── Worker 3（单线程 Event Loop）
    └── Worker N（= CPU 核数）

每个 Worker 可以同时处理数千个连接
连接由 OS 内核的 epoll/kqueue 管理
```

## 核心用途

```nginx
# 1. 反向代理
location /api/ {
    proxy_pass http://backend-server;
}

# 2. 负载均衡
upstream backend {
    server 192.168.1.10:8080 weight=3;
    server 192.168.1.11:8080 weight=1;
}

# 3. 限流
limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
limit_req zone=mylimit burst=20;

# 4. 静态资源 + 缓存
location /static/ {
    root /var/www;
    expires 30d;
}

# 5. SSL 终止（Nginx 处理 SSL，后端用 HTTP）
listen 443 ssl;
```""",
        "反向代理,负载均衡,epoll,Event Loop,C10K",
    )],
    "Docker": [(
        "Docker 的历史与核心原理",
        """## 起源

Docker 2013 年由 **dotCloud**（后改名 Docker Inc.）开源，创始人 Solomon Hykes。它让容器技术从"运维黑科技"变成"开发者日常"。

## 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| **Image** | 只读模板，包含运行环境 | 类（Class）|
| **Container** | Image 的运行实例 | 对象（Object）|
| **Dockerfile** | 构建 Image 的脚本 | Makefile |
| **Registry** | Image 仓库（Docker Hub / Harbor）| Maven 仓库 |
| **Volume** | 持久化存储 | 外挂硬盘 |

## 容器 vs 虚拟机

```
VM:      App → Guest OS → Hypervisor → Host OS
  每个 VM 要跑一个完整的 OS（浪费资源）

Container: App → Container Runtime → Host OS
  所有容器共享 Host OS 内核（轻量，秒级启动）
```

## 三大核心

| 技术 | 作用 |
|------|------|
| **Namespace** | 隔离（PID/Network/Mount/User...），每个容器看到自己的"世界"|
| **Cgroups** | 限制资源（CPU/内存/IO），防止一个容器吃光宿主机 |
| **UnionFS** | 分层文件系统，Image 可分多层，容器只加一层可写层 |

## Dockerfile 最佳实践

```dockerfile
FROM openjdk:17-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
# 不用 root 运行
RUN addgroup --system app && adduser --system --group app
USER app
ENTRYPOINT ["java", "-jar", "app.jar"]
```""",
        "镜像,容器,Namespace,Cgroups,UnionFS",
    )],
    "Prometheus + Grafana": [(
        "Prometheus + Grafana 监控体系",
        """## Prometheus

Prometheus 2012 年由 **SoundCloud** 开源，2016 年进入 CNCF，是继 Kubernetes 后第二个 CNCF 毕业项目。

### 核心原理：Pull 模型

```
Prometheus Server
    │ 定时抓取（scrape_interval: 15s）
    ↓
Target 1 (/actuator/prometheus)    Target 2 (/metrics)    Target 3 (node_exporter:9100)
```

**PromQL**（Prometheus Query Language）：
```promql
# QPS
rate(http_server_requests_seconds_count[1m])

# P99 延迟
histogram_quantile(0.99, rate(http_server_requests_seconds_bucket[5m]))

# 错误率
sum(rate(http_server_requests_seconds_count{status=~"5.."}[1m]))
  /
sum(rate(http_server_requests_seconds_count[1m]))
```

## Grafana

数据可视化平台，连接 Prometheus 做 Dashboard。

经典面板：
```
┌─────────────────────────────────┐
│ 服务 QPS (曲线图)                │
├─────────────────────────────────┤
│ P50 / P95 / P99 延迟 (曲线图)    │
├─────────────────┬───────────────┤
│ 错误率 (数字)    │ JVM 内存 (曲线)│
├─────────────────┴───────────────┤
│ 实例列表（健康/不健康）           │
└─────────────────────────────────┘
```

## 告警（AlertManager）

```yaml
groups:
  - name: app-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_errors[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "服务 {{ $labels.job }} 错误率超过 5%"
```""",
        "Prometheus,Grafana,PromQL,Pull模型,告警",
    )],
    "ELK (Elasticsearch + Logstash + Kibana)": [(
        "ELK 日志平台架构",
        """## ELK Stack

```
应用 1 ──→ Filebeat (轻量采集，解析日志)
应用 2 ──→ Filebeat                    │
应用 3 ──→ Filebeat                    │
                                       ↓
                              Logstash（过滤、转换、丰富字段）
                                       │
                                       ↓
                              Elasticsearch（存储 + 索引）
                                       │
                                       ↓
                              Kibana（查询、可视化、Dashboard）
```

## 各组件职责

| 组件 | 职责 | 替代 |
|------|------|------|
| **Filebeat** | 采集日志文件，低资源消耗 | Fluentd / Logstash |
| **Logstash** | 日志过滤和转换（grok 解析、geoip 丰富）| Fluentd |
| **Elasticsearch** | 存储 + 全文索引 | OpenSearch |
| **Kibana** | 查询 + Dashboard | Grafana 也在做日志 |

## 日志格式规范

```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "level": "ERROR",
  "service": "order-service",
  "instance": "order-service-7d8f9-abc123",
  "traceId": "a1b2c3d4e5f6",
  "message": "Failed to create order",
  "error": "Connection refused: inventory-service",
  "userId": "12345"
}
```

> 关键：日志中必须带 traceId，才能关联一条请求在多个服务中的完整日志链路。""",
        "日志,Filebeat,Logstash,Kibana,可观测性",
    )],
    "Jenkins": [(
        "Jenkins 持续集成核心概念",
        """## 起源

Jenkins 2011 年从 Hudson 分叉而来（Oracle 和社区关于 Hudson 名称的争议），现在是 CI/CD 领域最广泛使用的工具。

## 核心概念

```
Git Push
    │ Webhook
    ↓
Jenkins
    ├── Pipeline (Jenkinsfile)
    │   ├── Stage 1: Checkout（拉代码）
    │   ├── Stage 2: Build（mvn package）
    │   ├── Stage 3: Test（run tests）
    │   ├── Stage 4: SonarQube（代码扫描）
    │   ├── Stage 5: Build Image（docker build）
    │   ├── Stage 6: Push Image（推送到 Harbor）
    │   └── Stage 7: Deploy（kubectl apply）
    │
    └── 每个 Stage 在 Agent 上执行（Master 调度）
```

## Pipeline as Code

```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
            post {
                failure {
                    // 测试失败 → 发通知
                    emailext body: 'Tests failed!', subject: 'Build Failed',
                             to: 'team@example.com'
                }
            }
        }
        stage('Deploy') {
            when { branch 'main' }  // 只有 main 分支才部署
            steps {
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
```

## 替代方案

| 工具 | 特点 |
|------|------|
| **Jenkins** | 最成熟，插件生态丰富，需自行维护 |
| **GitLab CI** | GitLab 内置，配置简单 |
| **GitHub Actions** | GitHub 深度整合，开源项目首选 |
| **ArgoCD** | K8s 原生 GitOps，声明式持续部署 |""",
        "CI/CD,Pipeline,Jenkinsfile,DevOps",
    )],
    "MinIO": [(
        "MinIO 对象存储核心原理",
        """## 起源

MinIO 2014 年由 **Anand Babu Periasamy** 等人创建，是用 Go 语言编写的高性能对象存储，完全兼容 AWS S3 API。

## 核心特点

| 特点 | 说明 |
|------|------|
| **S3 兼容** | 直接替换 AWS S3，代码不用改 |
| **高性能** | Go 编写，单机读写 GB/s 级别 |
| **轻量** | 单个二进制文件，几十 MB |
| **纠删码** | 数据分片 + 校验码，N/2 块损坏也能恢复 |
| **分布式** | 多节点组成集群，自动负载均衡 |

## 部署方式

```bash
# Docker 部署（单机）
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=admin123 \
  quay.io/minio/minio server /data --console-address ":9001"

# 分布式部署（4 节点）
minio server http://node{1...4}/data{1...4}
```

## 典型用途

- **文件存储**：替代 FastDFS，存储用户上传的文件
- **静态资源**：前端静态文件、图片、视频
- **备份**：数据库备份文件、日志归档
- **制品仓库**：Maven/Docker/NPM 私有仓库（配合 Nexus 或直接使用）
- **AI/大数据**：训练数据集、模型文件存储

## vs FastDFS / OSS

| 维度 | MinIO | FastDFS | 阿里云 OSS |
|------|-------|---------|-----------|
| S3 兼容 | ✅ | ❌ | ✅ |
| 部署 | 简单（单二进制）| 复杂（Tracker+Storage+nginx）| 无需部署 |
| 社区 | 活跃 | 停更 | 商业服务 |
| 成本 | 免费（自建）| 免费（自建）| 按量付费 |""",
        "S3,对象存储,纠删码,分布式",
    )],
}

INTERVIEWS = {
    "Netty": [(
        "Netty 的 Reactor 模型是什么？为什么比传统 BIO 快？",
        """## Reactor 模型

Netty 采用**主从多 Reactor 模型**：

- Boss Group：专门 accept 新连接，分发给 Worker
- Worker Group：处理已建立连接的读写事件
- 每个 Reactor 线程一个 Selector，同时监听多个 Channel

## 为什么比 BIO 快

BIO（传统 Tomcat）：一个连接 = 一个线程 = 一个阻塞 IO。1000 个连接 = 1000 个线程。线程切换 + 栈内存开销巨大。

Netty NIO：一个线程可以管理数千个连接。只有真正有数据可读/可写的连接才占用 CPU。"线程成本"从 O(N) 降到 O(1)。""",
        "Reactor,NIO,BIO,EventLoop,高频",
    )],
    "RabbitMQ": [(
        "RabbitMQ 如何保证消息不丢失？",
        """## 消息丢失的三个环节

**生产端**：开启 Publisher Confirm 模式
```java
channel.confirmSelect();
channel.basicPublish(...);
channel.waitForConfirmsOrDie(5000);  // 等待 Broker ACK
```

**Broker 端**：队列和消息都持久化
```java
channel.queueDeclare("queue", true, false, false, null);  // durable=true
channel.basicPublish("", "queue",
    MessageProperties.PERSISTENT_TEXT_PLAIN,  // deliveryMode=2
    body);
```

**消费端**：手动 ACK
```java
boolean autoAck = false;
channel.basicConsume("queue", autoAck, (tag, delivery) -> {
    processMessage(delivery);
    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
}, tag -> {});
```

三管齐下 → 消息 100% 不丢失。""",
        "消息不丢失,Confirm,持久化,ACK,高频",
    )],
    "Kafka": [(
        "Kafka 为什么吞吐量这么高？",
        """## 四大原因

1. **顺序写磁盘**：Partition 日志是 append-only，顺序写磁盘比随机写快几十倍。现代 SSD 顺序写可达 500MB/s+。

2. **零拷贝**：数据从磁盘 → Page Cache → 网卡，用 `sendfile()` 系统调用绕过用户态，减少两次上下文切换。

3. **批量处理**：Producer 攒一批消息一起发，Consumer 一次拉取一批消息。batch.size 和 linger.ms 决定批量大小。

4. **Page Cache 依赖**：Kafka 严重依赖 OS 的 Page Cache 而非 JVM 堆内存。数据写入 Page Cache 就算"落盘"，由 OS 异步刷到磁盘。这就是为什么 Kafka 建议给 OS 留足够内存而不是给 JVM 堆。""",
        "吞吐量,零拷贝,顺序写,Page Cache,高频",
    )],
    "RocketMQ": [(
        "RocketMQ 的事务消息是怎么实现的？",
        """## 半消息机制

```
① Producer 发送 Half Message
    → Broker 存储消息，标记为"半消息"（Consumer 不可见）
② Producer 执行本地事务
③ 成功 → Commit Half Message → 标记为"可消费"
   失败 → Rollback → 删除消息
④ Broker 定时回查：
   如果长时间未收到 Commit/Rollback
      → 回调 Producer 的 checkLocalTransaction()
      → 根据返回值决定 Commit 还是 Rollback
```

配套 JDBC 事务：
```java
// RocketMQ + JDBC 事务
@RocketMQTransactionListener
public TransactionListener txListener = new TransactionListener() {
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        // 在这里操作 DB + 发消息在同一个本地事务中
        orderDao.insert(order);
        return LocalTransactionState.COMMIT;
    }
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        // 回查时检查 DB 是否有对应记录
        return orderDao.exists(msg.getKeys()) ? COMMIT : ROLLBACK;
    }
};
```""",
        "事务消息,半消息,回查,高频",
    )],
    "Redis": [(
        "Redis 缓存穿透/击穿/雪崩怎么解决？",
        """## 穿透：查不存在的数据

**问题**：恶意请求大量不存在的 key → 每次都查 DB
**解决**：
- 布隆过滤器：先判断 key 是否可能存在，不存在直接拒绝
- 空值缓存：null 也缓存（TTL 设短，如 60 秒）

## 击穿：热点 key 过期

**问题**：秒杀商品的缓存刚好过期 → 瞬间流量打爆 DB
**解决**：
- 互斥锁：第一个请求拿到锁去查 DB，其他请求等待
- 逻辑过期：永不过期 + 后台线程异步刷新

## 雪崩：大量 key 同时过期

**问题**：批量缓存设置了相同的 TTL → 同时过期
**解决**：
- TTL 加随机值：30min + random(0, 5min)
- 多级缓存：本地 Caffeine → Redis → DB
- 限流降级：Sentinel 保护 DB""",
        "穿透,击穿,雪崩,缓存,高频",
    )],
    "Elasticsearch": [(
        "ES 的写入和查询流程是怎样的？",
        """## 写入流程

```
Client → 协调节点
  → 计算: doc_id % shard_count → Shard X
  → 路由到 Primary Shard X
  → 写入 Lucene IndexSegment（内存）
  → refresh（默认 1s）→ 变为可搜索
  → 同步到 Replica Shards
  → translog fsync → 持久化到磁盘
```

## 查询流程

```
Client → 协调节点
  → 广播查询到所有相关 Shard
  → 每个 Shard 在自己的 Lucene 索引中搜索 → 返回 Top N
  → 协调节点合并排序 → 取全局 Top N
  → 根据 doc_id 去对应 Shard 获取完整 Document
```

> 关键：ES 近实时（1s refresh），不是实时的。实时场景用 Redis。""",
        "写入,查询,refresh,分片,高频",
    )],
    "MySQL": [(
        "MySQL 的 MVCC 是如何实现的？",
        """## MVCC 原理

每条记录有两个隐藏列：
- `DB_TRX_ID`：最后修改这条记录的事务 ID
- `DB_ROLL_PTR`：指向 Undo Log 的回滚指针

```
当前记录: id=1, name='Bob', DB_TRX_ID=105
Undo Log: id=1, name='Alice', DB_TRX_ID=103 → id=1, name=NULL, DB_TRX_ID=100

事务 106（ReadView = [活跃事务: 104, 105]）查询时：
  当前记录 TRX_ID=105 是活跃事务 → 不可见
  → 沿着 DB_ROLL_PTR 找到 Undo Log
  → TRX_ID=103 < ReadView 最小活跃事务 → 可见 → 返回 'Alice'
```

RR（可重复读）级别：事务开始时生成一次 ReadView
RC（读已提交）级别：每次查询都重新生成 ReadView

这就是为什么 RR 下同一事务内的两次 SELECT 结果一致（都用同一个 ReadView）。""",
        "MVCC,ReadView,Undo Log,隔离级别,高频",
    )],
    "Docker": [(
        "Docker 镜像的层是什么？为什么要分层？",
        """## 分层结构

```dockerfile
FROM ubuntu:22.04          ← Layer 1: 基础层（只读）
RUN apt-get update          ← Layer 2: 更新层（只读）
COPY app.jar /app/          ← Layer 3: 应用层（只读）
CMD ["java", "-jar"]        ← 元数据（不占空间）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Container 运行 → 可写层（Container Layer）
```

## 分层的好处

1. **复用**：多个镜像共享同一基础层（ubuntu:22.04 只存一份）
2. **快速构建**：只重建变化的层（改 jar → 只重建 Layer 3，Layer 1、2 用缓存）
3. **快速分发**：pull 镜像时，已存在的层不需要重新下载

> Dockerfile 最佳实践：把不常变的放在前面（OS → 依赖 → 应用代码），充分利用缓存。""",
        "镜像层,UnionFS,缓存,构建优化,高频",
    )],
}


def seed():
    db = get_db()
    tool = db.execute("SELECT id FROM tool WHERE name = '面试储备'").fetchone()
    if not tool:
        print("Tool not found!"); return
    tid = tool["id"]

    db.execute("DELETE FROM entry WHERE stack_id IN (SELECT id FROM stack WHERE group_name='中间件')")
    db.execute("DELETE FROM stack WHERE group_name='中间件'")

    for name, desc, order, deprecated in STACKS:
        db.execute(
            "INSERT INTO stack (tool_id, name, description, sort_order, is_deprecated, group_name) VALUES (?,?,?,?,?,'中间件')",
            (tid, name, desc, order, deprecated),
        )
    db.commit()

    tn = ti = 0
    for stack_name, note_list in NOTES.items():
        row = db.execute("SELECT id FROM stack WHERE name=? AND group_name='中间件'", (stack_name,)).fetchone()
        if not row: continue
        sid = row["id"]
        for title, content, tags in note_list:
            db.execute("INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?,?,?,?,'note')", (sid, title, content, tags))
        tn += len(note_list)
        iv_list = INTERVIEWS.get(stack_name, [])
        for title, content, tags in iv_list:
            db.execute("INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?,?,?,?,'interview')", (sid, title, content, tags))
        ti += len(iv_list)
        db.commit()
        print(f"  OK {stack_name}: {len(note_list)} notes + {len(iv_list)} interviews")

    db.close()
    print(f"\nTotal: {len(STACKS)} stacks, {tn} notes, {ti} interviews")


if __name__ == "__main__":
    seed()
