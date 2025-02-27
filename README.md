# Python装饰器教程与示例

本项目提供了Python装饰器的详细教程和实际应用示例，特别是在FastAPI框架中的应用。

## 什么是装饰器？

装饰器是Python中一种强大的编程模式，它允许我们在不修改原始函数代码的情况下，增强或修改函数的行为。装饰器本质上是一个接受函数作为参数并返回一个新函数的高阶函数。

### 装饰器的基本语法

```python
@decorator_name
def function_name():
    pass
```

这等同于：

```python
def function_name():
    pass

function_name = decorator_name(function_name)
```

## 项目结构

```
src/
├── common/
│   └── base_models/
│       └── tenant_mixin.py  # 包含装饰器基本概念的注释
├── examples/
│   ├── decorator_examples.py  # 基础装饰器示例
│   └── fastapi_decorators.py  # FastAPI中的装饰器应用
└── README.md  # 本文件
```

## 装饰器类型

本项目包含以下类型的装饰器示例：

### 1. 基本装饰器

最简单的装饰器形式，不接受参数，直接修改函数行为。

```python
@simple_decorator
def greet(name):
    return f"你好, {name}!"
```

### 2. 带参数的装饰器

可以接受配置参数的装饰器。

```python
@repeat(times=3)
def say_hello(name):
    return f"你好, {name}!"
```

### 3. 类装饰器

使用类实现的装饰器，通过`__init__`和`__call__`方法实现。

```python
@Timer
def slow_function():
    time.sleep(1)
    print("耗时操作完成")
```

### 4. 装饰器链

多个装饰器可以链式应用，从下到上执行。

```python
@decorator1
@decorator2
def function():
    pass
```

## FastAPI中的装饰器应用

本项目展示了FastAPI中常用的装饰器模式：

1. **租户ID验证装饰器** - 验证请求中是否包含有效的租户ID
2. **权限验证装饰器** - 验证用户是否拥有所需权限
3. **请求日志装饰器** - 记录API请求的详细信息
4. **缓存装饰器** - 缓存API响应结果
5. **租户数据过滤装饰器** - 自动过滤返回结果中的租户数据
6. **组合装饰器** - 将多个装饰器组合成一个便捷的装饰器

## 运行示例

### 基础装饰器示例

```bash
python src/examples/decorator_examples.py
```

### FastAPI装饰器示例

```bash
python src/examples/fastapi_decorators.py
```

## 装饰器最佳实践

1. **使用functools.wraps** - 保留原始函数的元数据（如函数名、文档字符串等）
2. **类型提示** - 使用TypeVar和cast确保类型安全
3. **文档化** - 为装饰器提供清晰的文档字符串
4. **错误处理** - 在装饰器中妥善处理异常
5. **避免副作用** - 装饰器应该尽量避免修改全局状态

## 常见应用场景

1. **日志记录** - 记录函数调用、参数和返回值
2. **性能监控** - 测量函数执行时间
3. **访问控制** - 验证用户权限
4. **缓存** - 缓存函数结果以提高性能
5. **重试机制** - 在失败时自动重试函数
6. **事务管理** - 在数据库操作中管理事务
7. **输入验证** - 验证函数参数

## 进阶主题

1. **装饰器工厂** - 创建可配置的装饰器
2. **类方法装饰器** - 装饰类方法
3. **装饰器类** - 使用类实现装饰器
4. **保留函数签名** - 使用inspect模块保留函数签名
5. **异步装饰器** - 装饰异步函数

## 参考资料

- [Python官方文档 - 装饰器](https://docs.python.org/zh-cn/3/glossary.html#term-decorator)
- [PEP 318 -- 函数和方法的装饰器](https://www.python.org/dev/peps/pep-0318/)
- [FastAPI官方文档](https://fastapi.tiangolo.com/zh/)