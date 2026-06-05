"""初始化种子数据：面试储备工具 + Spring Cloud 技术栈（按学习路线排序）"""
from db import init_db, get_db


def seed():
    init_db()
    db = get_db()

    # 删除旧数据，重新初始化
    db.execute("DELETE FROM entry")
    db.execute("DELETE FROM stack")
    db.execute("DELETE FROM tool")

    # 创建工具
    db.execute(
        "INSERT INTO tool (id, name, description) VALUES (1, '面试储备', 'Java Spring Cloud 面试技术栈积累')"
    )

    # 技术栈按学习路线排序：(name, description, sort_order, is_deprecated)
    stacks = [
        # ===== P0: 前置基础 =====
        ("Spring Boot", "Spring Cloud 微服务的地基，自动配置、起步依赖、Actuator、外部化配置，面试必问", 0, 0),

        # ===== Phase 1: 基础入门 =====
        ("Spring Cloud Alibaba Nacos", "服务注册发现 + 配置中心，替代 Eureka+Config 的现代方案，CP+AP 双模式", 1, 0),
        ("Spring Cloud OpenFeign", "声明式 HTTP 客户端，集成 LoadBalancer，远程调用首选", 2, 0),
        ("Spring Cloud LoadBalancer", "客户端负载均衡，Spring 官方替代 Ribbon，与 Feign 无缝集成", 3, 0),

        # ===== Phase 2: 高可用与容错 =====
        ("Spring Cloud Alibaba Sentinel", "流量控制、熔断降级、系统自适应保护，比 Hystrix 更强大", 4, 0),
        ("Resilience4j", "轻量级容错库，熔断/限流/重试/隔离舱，Spring 官方推荐", 5, 0),
        ("Spring Cloud Circuit Breaker", "熔断器抽象层，统一 Sentinel/Resilience4j 的编程模型", 6, 0),

        # ===== Phase 3: 网关与配置 =====
        ("Spring Cloud Gateway", "API 网关，基于 WebFlux 异步非阻塞，替代 Zuul", 7, 0),
        ("Spring Cloud Config", "分布式配置中心，Git/SVN 存储，配合 Bus 实现动态刷新", 8, 0),
        ("Spring Cloud Bus", "消息总线，通过 RabbitMQ/Kafka 广播配置变更", 9, 0),

        # ===== Phase 4: 消息与可观测性 =====
        ("Spring Cloud Stream", "消息驱动微服务，统一 RabbitMQ/Kafka 编程模型", 10, 0),
        ("SkyWalking", "Apache 分布式 APM，链路追踪+性能监控+拓扑图，生产级方案", 11, 0),
        ("Micrometer Tracing", "Spring 官方链路追踪方案（Sleuth 的继任者），集成 Brave/OpenTelemetry，推荐新项目使用", 12, 0),

        # ===== Phase 5: 高级主题 =====
        ("Spring Cloud Alibaba Seata", "分布式事务：AT/TCC/Saga/XA 四种模式", 13, 0),
        ("MyBatis-Plus", "MyBatis 增强工具，无侵入 CRUD、分页、逻辑删除，Spring Boot 数据层标配", 14, 0),
        ("Spring Cloud Kubernetes", "Spring Cloud on K8s，使用 K8s 原生服务发现和配置", 15, 0),
        ("Spring Boot Admin", "Spring Boot 应用监控管理平台，可视化运行状态", 16, 0),
        ("Spring Cloud Task", "短生命周期微服务，适合批处理/定时任务", 17, 0),
        ("Spring Cloud Contract", "消费者驱动契约测试（CDC），保证 API 兼容性", 18, 0),

        # ===== 了解即可（过时技术 / 已停更）=====
        ("Spring Cloud Sleuth", "❌ 项目已归档，核心迁移到 Micrometer Tracing，了解其 TraceId/SpanId 传播机制即可", 19, 1),
        ("Spring Security OAuth2", "❌ 旧独立项目已废弃，OAuth2 功能已内置到 Spring Security 5.x（oauth2-client / oauth2-resource-server），学新不用学旧", 20, 1),
        ("Spring Cloud Netflix Ribbon", "❌ 已停更，客户端负载均衡的历史方案，了解轮询/随机策略思想即可，现在用 LoadBalancer", 21, 1),
        ("Spring Cloud Netflix Hystrix", "❌ 已停更，熔断降级的历史方案，了解断路器模式思想即可，现在用 Sentinel / Resilience4j", 22, 1),
        ("Spring Cloud Netflix Zuul", "❌ 已停更，API 网关的历史方案（Servlet 阻塞模型），了解网关职责即可，现在用 Gateway", 23, 1),
        ("Spring Cloud Netflix Eureka", "❌ 已进入维护模式，服务注册发现的历史方案，了解 CAP 中 AP 模型的取舍思想即可，现在用 Nacos", 24, 1),
    ]

    for name, desc, order, deprecated in stacks:
        db.execute(
            "INSERT INTO stack (tool_id, name, description, sort_order, is_deprecated) VALUES (1, ?, ?, ?, ?)",
            (name, desc, order, deprecated),
        )

    db.commit()
    db.close()
    print("Seed data initialized!")
    print(f"   Tool: mianshichubei")
    print(f"   Stacks: {len(stacks)} (active: {len([s for s in stacks if s[3]==0])}, deprecated: {len([s for s in stacks if s[3]==1])})")


if __name__ == "__main__":
    seed()
