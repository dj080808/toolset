"""初始化种子数据：面试储备工具 + Spring Cloud 技术栈"""
from db import init_db, get_db


def seed():
    init_db()
    db = get_db()

    # 创建工具
    db.execute(
        "INSERT OR IGNORE INTO tool (id, name, description) VALUES (1, '面试储备', 'Java Spring Cloud 面试技术栈积累')"
    )

    # Spring Cloud 技术栈列表
    stacks = [
        ("Spring Cloud Gateway", "API 网关，基于 WebFlux 的响应式网关，替代 Zuul"),
        ("Spring Cloud Netflix Eureka", "服务注册与发现，AP 模型，支持自我保护模式"),
        ("Spring Cloud OpenFeign", "声明式 HTTP 客户端，集成 Ribbon 负载均衡"),
        ("Spring Cloud LoadBalancer", "客户端负载均衡器，Spring 官方替代 Ribbon 的方案"),
        ("Spring Cloud Circuit Breaker", "熔断器抽象层，支持 Resilience4j、Sentinel 等实现"),
        ("Resilience4j", "轻量级容错库，提供熔断、限流、重试、隔离舱"),
        ("Spring Cloud Config", "分布式配置中心，支持 Git/SVN/本地文件存储配置"),
        ("Spring Cloud Bus", "消息总线，通过 MQ 广播配置变更，实现动态刷新"),
        ("Spring Cloud Stream", "消息驱动微服务框架，统一 MQ 编程模型（RabbitMQ/Kafka）"),
        ("Spring Cloud Sleuth", "分布式链路追踪，集成 Zipkin/Brave"),
        ("Spring Cloud Alibaba Nacos", "阿里巴巴开源的服务发现与配置管理平台"),
        ("Spring Cloud Alibaba Sentinel", "流量控制、熔断降级、系统负载保护"),
        ("Spring Cloud Alibaba Seata", "分布式事务解决方案（AT/TCC/Saga/XA 模式）"),
        ("Spring Cloud Kubernetes", "将 Spring Cloud 应用部署到 K8s，使用 K8s 原生服务发现"),
        ("Spring Cloud Task", "短生命周期微服务，适合批处理任务"),
        ("Spring Cloud Contract", "消费者驱动契约测试（CDC），确保 API 兼容性"),
        ("Spring Security OAuth2", "认证授权，支持 OAuth2/OIDC，集成 JWT"),
        ("Spring Boot Admin", "Spring Boot 应用监控管理平台"),
        ("SkyWalking", "Apache 分布式 APM 系统，链路追踪与性能监控"),
    ]

    for i, (name, desc) in enumerate(stacks):
        db.execute(
            "INSERT OR IGNORE INTO stack (tool_id, name, description, sort_order) VALUES (1, ?, ?, ?)",
            (name, desc, i),
        )

    db.commit()
    db.close()
    print("Seed data initialized!")
    print(f"   Tool: mianshichubei")
    print(f"   Stacks: {len(stacks)}")


if __name__ == "__main__":
    seed()
