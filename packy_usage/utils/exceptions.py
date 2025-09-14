"""
自定义异常类
"""


class PackyUsageError(Exception):
    """基础异常类"""
    pass


class ConfigError(PackyUsageError):
    """配置相关异常"""
    pass


class SecurityError(PackyUsageError):
    """安全相关异常"""
    pass


class ApiError(PackyUsageError):
    """API调用异常"""
    pass


class NetworkError(PackyUsageError):
    """网络连接异常"""
    pass


class AuthError(ApiError):
    """认证失败异常"""
    pass


class ValidationError(PackyUsageError):
    """数据验证异常"""
    pass


class UIError(PackyUsageError):
    """用户界面异常"""
    pass