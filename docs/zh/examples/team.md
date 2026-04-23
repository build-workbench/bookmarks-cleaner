# 团队配置

在团队中共享统一的 CleanBook 配置。

## 配置仓库

创建一个 Git 仓库管理团队配置：

```
team-config/
├── config.json          # 团队统一配置
├── taxonomy/
│   ├── subjects.yaml    # 主题分类词表
│   └── companies.yaml   # 公司域名映射
└── README.md
```

## 共享配置

### 方式一：Git 子模块

```bash
# 在项目仓库中添加配置子模块
git submodule add https://github.com/your-team/cleanbook-config.git config/cleanbook

# 创建符号链接
ln -s config/cleanbook/config.json config.json
```

### 方式二：配置文件下载

```bash
# 从内部 CDN 下载
curl -O https://internal.company.com/cleanbook/config.json
```

### 方式三：容器镜像

将配置文件打包到团队 Docker 镜像：

```dockerfile
FROM python:3.11-slim

COPY team-config/ /etc/cleanbook/
RUN pip install cleanbook

ENV CLEANBOOK_CONFIG=/etc/cleanbook/config.json

ENTRYPOINT ["cleanbook"]
```

## 配置版本管理

```bash
# 配置文件版本
cleanbook --show-config | grep "version"

# 检查配置更新
curl -s https://internal.company.com/cleanbook/config.json | diff config.json -
```

## 成员使用

```bash
# 拉取最新配置
git submodule update --remote

# 运行清理
cleanbook -i bookmarks.html -o output/
```
