"""Dubbo 技术栈组：学习路线、知识笔记、面试题"""
from db import get_db


def seed():
    db = get_db()

    tid = db.execute("SELECT id FROM tool WHERE name = '面试储备'").fetchone()
    if not tid:
        print("Tool not found!")
        return
    tool_id = tid["id"]

    # 删旧
    db.execute("DELETE FROM entry WHERE stack_id IN (SELECT id FROM stack WHERE group_name='Dubbo')")
    db.execute("DELETE FROM stack WHERE group_name='Dubbo'")

    stacks = [
        # P0: 前置基础
        ("Dubbo 概述与 RPC 原理", "Apache Dubbo 高性能 RPC 框架的历史、核心概念与 RPC 基础原理", 0, 0),
        # P1: 核心基础
        ("Dubbo 服务注册与发现", "注册中心（ZooKeeper/Nacos/Redis）、服务导出与服务引用流程", 1, 0),
        ("Dubbo 通信协议", "Dubbo/Triple/REST/gRPC 协议对比，TCP 长连接与多路复用", 2, 0),
        ("Dubbo 序列化机制", "Hessian2、FastJSON2、Protobuf、Kryo 序列化方案对比与选型", 3, 0),
        # P2: 服务治理
        ("Dubbo 集群容错", "Failover/Failfast/Failsafe/Failback/Forking/Broadcast 六大策略", 4, 0),
        ("Dubbo 负载均衡", "Random/RoundRobin/LeastActive/ConsistentHash 四种策略与原理", 5, 0),
        ("Dubbo 服务路由与治理", "条件路由、标签路由、动态配置、权重调整、灰度发布", 6, 0),
        # P3: 高级特性
        ("Dubbo SPI 扩展机制", "Dubbo 微内核 + 插件式架构，自适应扩展与激活机制", 7, 0),
        ("Dubbo 异步调用与泛化调用", "CompletableFuture 异步、Reactor 响应式、泛化调用原理", 8, 0),
        ("Dubbo 线程模型与性能优化", "IO 线程池、业务线程池、线程派发策略、参数调优", 9, 0),
        # P4: 生态与运维
        ("Dubbo Admin 控制台", "Dubbo 官方管理控制台的部署与使用，服务治理可视化", 10, 0),
        ("Dubbo 3.x 核心新特性", "应用级服务发现、Triple 协议、云原生支持、3.0 架构重构", 11, 0),
        ("Dubbo + Sentinel 流量控制", "Dubbo 集成 Sentinel 实现限流降级，保护服务稳定性", 12, 0),
    ]

    for name, desc, order, deprecated in stacks:
        db.execute(
            "INSERT INTO stack (tool_id, name, description, sort_order, is_deprecated, group_name) VALUES (?,?,?,?,?,'Dubbo')",
            (tool_id, name, desc, order, deprecated),
        )
    db.commit()

    # 填充内容
    _seed_content(db)
    db.close()


def _seed_content(db):
    """填充各技术栈条目"""
    from seed_dubbo_content import seed_all
    seed_all(db)


if __name__ == "__main__":
    seed()
