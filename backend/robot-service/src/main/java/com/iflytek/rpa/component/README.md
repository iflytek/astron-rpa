# Component 组件模块

## 概述
Component模块提供了完整的组件管理功能，包括组件的增删改查、状态管理、权限控制等。

## 功能特性
- 组件的创建、更新、删除、查询
- 组件名称重复检查
- 组件状态管理（编辑中、已发版、已上架、锁定）
- 组件来源管理（自己创建、市场获取）
- 分页查询和条件筛选
- 租户隔离和用户权限控制

## 文件结构
```
src/main/java/com/iflytek/rpa/component/
├── constants/
│   └── ComponentConstant.java          # 组件常量定义
├── controller/
│   └── ComponentController.java        # 控制器层
├── dao/
│   └── ComponentDao.java               # 数据访问层接口
├── entity/
│   ├── Component.java                  # 组件实体类
│   ├── dto/
│   │   └── ComponentQueryDto.java      # 查询DTO
│   ├── enums/
│   │   └── ComponentStatusEnum.java    # 状态枚举
│   └── vo/
│       └── ComponentVo.java            # 视图对象
├── service/
│   ├── ComponentService.java           # 服务接口
│   └── impl/
│       └── ComponentServiceImpl.java   # 服务实现
└── README.md                           # 说明文档
```

## 数据库表结构
```sql
CREATE TABLE component (
    id               BIGINT AUTO_INCREMENT COMMENT '主键id' PRIMARY KEY,
    component_id     VARCHAR(100) NULL COMMENT '机器人唯一id，获取的应用id',
    name             VARCHAR(100) NULL COMMENT '当前名字，用于列表展示',
    creator_id       BIGINT NULL COMMENT '创建者id',
    create_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL COMMENT '创建时间',
    updater_id       BIGINT NULL COMMENT '更新者id',
    update_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_shown         SMALLINT(1) DEFAULT 1 NULL COMMENT '是否在用户列表页显示 0：不显示，1：显示',
    deleted          SMALLINT(1) DEFAULT 0 NULL COMMENT '是否删除 0：未删除，1：已删除',
    tenant_id        BIGINT NULL,
    app_id           VARCHAR(50) CHARSET utf8mb4 NULL COMMENT 'appmarketResource中的应用id',
    app_version      INT NULL COMMENT '获取的应用：应用市场版本',
    market_id        VARCHAR(20) CHARSET utf8mb4 NULL COMMENT '获取的应用：市场id',
    resource_status  VARCHAR(20) NULL COMMENT '资源状态：toObtain, obtained, toUpdate',
    data_source      VARCHAR(20) NULL COMMENT '来源：create 自己创建 ； market 市场获取',
    transform_status VARCHAR(20) NULL COMMENT 'editing 编辑中，published 已发版，shared 已上架，locked锁定（无法编辑）'
) COMMENT '组件表' CHARSET = utf8;
```

## API接口

### 1. 创建组件
- **接口**: `POST /component/create`
- **参数**: Component对象
- **功能**: 创建新的组件

### 2. 更新组件
- **接口**: `POST /component/update`
- **参数**: Component对象
- **功能**: 更新现有组件信息

### 3. 删除组件
- **接口**: `DELETE /component/delete/{componentId}`
- **参数**: componentId (路径参数)
- **功能**: 逻辑删除组件

### 4. 查询组件详情
- **接口**: `GET /component/detail/{componentId}`
- **参数**: componentId (路径参数)
- **功能**: 根据ID查询组件详情

### 5. 分页查询组件列表
- **接口**: `GET /component/list`
- **参数**: pageNum, pageSize, name (可选)
- **功能**: 分页查询组件列表，支持名称模糊查询

### 6. 重命名组件
- **接口**: `PUT /component/rename`
- **参数**: componentId, newName
- **功能**: 重命名组件

### 7. 检查名称重复
- **接口**: `GET /component/check-name`
- **参数**: name, componentId (可选)
- **功能**: 检查组件名称是否重复

### 8. 更新组件状态
- **接口**: `PUT /component/status`
- **参数**: componentId, transformStatus
- **功能**: 更新组件的转换状态

### 9. 获取我的组件列表
- **接口**: `GET /component/my-list`
- **功能**: 获取当前用户创建的组件列表

## 状态说明

### 资源状态 (resourceStatus)
- `toObtain`: 待获取
- `obtained`: 已获取
- `toUpdate`: 待更新

### 数据来源 (dataSource)
- `create`: 自己创建
- `market`: 市场获取

### 转换状态 (transformStatus)
- `editing`: 编辑中
- `published`: 已发版
- `shared`: 已上架
- `locked`: 锁定

## 使用示例

### 创建组件
```java
Component component = new Component();
component.setName("测试组件");
component.setAppId("app123");
component.setMarketId("market456");

AppResponse<?> response = componentService.createComponent(component);
```

### 查询组件列表
```java
AppResponse<?> response = componentService.getComponentList(1, 10, "测试");
```

### 更新组件状态
```java
AppResponse<?> response = componentService.updateComponentStatus("comp123", "published");
```

## 注意事项
1. 所有操作都需要用户登录和租户权限验证
2. 组件名称在同一租户下不能重复
3. 删除操作采用逻辑删除，不会物理删除数据
4. 组件状态变更需要相应的权限控制
5. 支持租户隔离，不同租户的数据相互独立

## 依赖说明
- MyBatis-Plus: 数据访问层框架
- Spring Boot: 应用框架
- Lombok: 代码简化工具
- Validation: 参数验证 