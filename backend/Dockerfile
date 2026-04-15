FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 先只复制依赖文件，利用 Docker 缓存层
COPY pyproject.toml .
RUN mkdir -p app && touch app/__init__.py
# 普通安装（不用 -e），避免 volume mount 覆盖时找不到包
RUN pip install --no-cache-dir ".[dev]"

# 再复制源代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
