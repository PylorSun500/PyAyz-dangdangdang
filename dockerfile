FROM python:3.14-slim-bookworm

# 系统工具包
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 基础工具
    curl wget git vim htop procps \
    # 网络调试
    netcat-openbsd dnsutils iproute2 \
    # 构建依赖（pandas/numpy 需要）
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /workspace

#  Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    # 额外常用交互工具
    && pip install --no-cache-dir \
        ipython \
        jupyter \
        pytest \
        black \
        flake8

# 启动脚本（开发模式）
EXPOSE 5001

# 默认进入交互式 Shell（也可通过 docker-compose 覆盖）
CMD ["/bin/bash"]
