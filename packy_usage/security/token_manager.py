"""
Token 安全存储管理器
使用系统密钥管理服务安全存储API Token
"""

import json
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

import keyring
from keyring.errors import KeyringError

from ..utils.logger import get_logger
from ..utils.exceptions import SecurityError

logger = get_logger(__name__)


class TokenType(Enum):
    """Token类型"""
    UNKNOWN = "unknown"
    API_KEY = "api_key"      # sk- 开头的API Key
    JWT = "jwt"              # JWT格式的临时Token


class TokenManager:
    """Token管理器"""
    
    SERVICE_NAME = "packy-usage-monitor"
    TOKEN_KEY = "api_token" 
    TOKEN_META_KEY = "token_metadata"
    
    def __init__(self):
        self._validate_keyring()
    
    def _validate_keyring(self):
        """验证密钥环是否可用"""
        try:
            # 测试密钥环功能
            test_key = f"{self.SERVICE_NAME}_test"
            keyring.set_password(self.SERVICE_NAME, test_key, "test")
            keyring.delete_password(self.SERVICE_NAME, test_key)
            logger.debug("密钥环功能正常")
        except KeyringError as e:
            logger.warning(f"密钥环不可用，将使用备用存储: {e}")
    
    def save_token(self, token: str) -> bool:
        """
        保存Token到安全存储
        
        Args:
            token: API Token字符串
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if not token or not token.strip():
                raise ValueError("Token不能为空")
            
            token = token.strip()
            
            # 检测Token类型
            token_type = self._detect_token_type(token)
            
            # 准备元数据
            metadata = {
                "type": token_type.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_validated": None
            }
            
            # 如果是JWT，尝试解析过期时间
            if token_type == TokenType.JWT:
                exp_time = self._extract_jwt_expiration(token)
                if exp_time:
                    metadata["expires_at"] = exp_time.isoformat()
            
            # 保存Token和元数据
            keyring.set_password(self.SERVICE_NAME, self.TOKEN_KEY, token)
            keyring.set_password(self.SERVICE_NAME, self.TOKEN_META_KEY, json.dumps(metadata))
            
            logger.info(f"Token已安全保存 (类型: {token_type.value})")
            return True
            
        except KeyringError as e:
            logger.error(f"保存Token失败 (密钥环错误): {e}")
            raise SecurityError(f"无法保存Token: {e}")
        except Exception as e:
            logger.error(f"保存Token失败: {e}")
            raise SecurityError(f"保存Token失败: {e}")
    
    def get_token(self) -> Optional[str]:
        """
        从安全存储获取Token
        
        Returns:
            Optional[str]: Token字符串，如果不存在返回None
        """
        try:
            token = keyring.get_password(self.SERVICE_NAME, self.TOKEN_KEY)
            
            if not token:
                logger.debug("未找到存储的Token")
                return None
            
            # 检查Token是否过期
            if self._is_token_expired():
                logger.warning("Token已过期，自动清理")
                self.delete_token()
                return None
            
            return token
            
        except KeyringError as e:
            logger.error(f"获取Token失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取Token时发生未知错误: {e}")
            return None
    
    def delete_token(self) -> bool:
        """
        删除存储的Token
        
        Returns:
            bool: 删除是否成功
        """
        try:
            # 删除Token
            try:
                keyring.delete_password(self.SERVICE_NAME, self.TOKEN_KEY)
            except KeyringError:
                pass  # Token可能已经不存在
            
            # 删除元数据
            try:
                keyring.delete_password(self.SERVICE_NAME, self.TOKEN_META_KEY)
            except KeyringError:
                pass  # 元数据可能已经不存在
            
            logger.info("Token已从安全存储中删除")
            return True
            
        except Exception as e:
            logger.error(f"删除Token失败: {e}")
            return False
    
    def get_token_type(self) -> TokenType:
        """
        获取Token类型
        
        Returns:
            TokenType: Token类型
        """
        try:
            metadata_str = keyring.get_password(self.SERVICE_NAME, self.TOKEN_META_KEY)
            if not metadata_str:
                return TokenType.UNKNOWN
            
            metadata = json.loads(metadata_str)
            return TokenType(metadata.get("type", TokenType.UNKNOWN.value))
            
        except Exception as e:
            logger.debug(f"无法获取Token类型: {e}")
            return TokenType.UNKNOWN
    
    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """
        获取Token信息
        
        Returns:
            Optional[Dict]: Token信息，包括类型、创建时间等
        """
        try:
            metadata_str = keyring.get_password(self.SERVICE_NAME, self.TOKEN_META_KEY)
            if not metadata_str:
                return None
            
            metadata = json.loads(metadata_str)
            
            # 添加当前状态信息
            info = metadata.copy()
            info["exists"] = self.get_token() is not None
            info["expired"] = self._is_token_expired()
            
            return info
            
        except Exception as e:
            logger.debug(f"无法获取Token信息: {e}")
            return None
    
    def get_token_expiration(self, token: Optional[str] = None) -> Optional[datetime]:
        """
        获取Token过期时间
        
        Args:
            token: Token字符串，如果为None则使用存储的Token
            
        Returns:
            Optional[datetime]: 过期时间，如果无法确定返回None
        """
        if not token:
            token = self.get_token()
        
        if not token:
            return None
        
        token_type = self._detect_token_type(token)
        
        if token_type == TokenType.JWT:
            return self._extract_jwt_expiration(token)
        
        # API Key没有过期时间
        return None
    
    def _detect_token_type(self, token: str) -> TokenType:
        """检测Token类型"""
        if token.startswith("sk-"):
            return TokenType.API_KEY
        elif self._is_jwt_format(token):
            return TokenType.JWT
        else:
            return TokenType.UNKNOWN
    
    def _is_jwt_format(self, token: str) -> bool:
        """检查是否为JWT格式"""
        try:
            parts = token.split(".")
            return len(parts) == 3
        except:
            return False
    
    def _extract_jwt_expiration(self, token: str) -> Optional[datetime]:
        """提取JWT的过期时间"""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            
            # 解码payload部分
            payload_part = parts[1]
            # JWT使用URL-safe base64编码
            payload_part += '=' * (4 - len(payload_part) % 4)  # 添加填充
            payload_bytes = base64.urlsafe_b64decode(payload_part.encode())
            payload = json.loads(payload_bytes.decode())
            
            # 提取过期时间
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp, timezone.utc)
            
            return None
            
        except Exception as e:
            logger.debug(f"解析JWT过期时间失败: {e}")
            return None
    
    def _is_token_expired(self) -> bool:
        """检查Token是否过期"""
        try:
            metadata_str = keyring.get_password(self.SERVICE_NAME, self.TOKEN_META_KEY)
            if not metadata_str:
                return False
            
            metadata = json.loads(metadata_str)
            expires_at_str = metadata.get("expires_at")
            
            if not expires_at_str:
                # 没有过期时间信息，认为未过期
                return False
            
            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            return datetime.now(timezone.utc) >= expires_at
            
        except Exception as e:
            logger.debug(f"检查Token过期状态失败: {e}")
            return False
    
    def validate_token_format(self, token: str) -> tuple[bool, str]:
        """
        验证Token格式
        
        Args:
            token: Token字符串
            
        Returns:
            tuple[bool, str]: (是否有效, 错误信息)
        """
        if not token or not token.strip():
            return False, "Token不能为空"
        
        token = token.strip()
        
        # 检查API Key格式
        if token.startswith("sk-"):
            if len(token) < 10:
                return False, "API Key格式无效"
            return True, ""
        
        # 检查JWT格式
        if self._is_jwt_format(token):
            try:
                exp_time = self._extract_jwt_expiration(token)
                if exp_time and datetime.now(timezone.utc) >= exp_time:
                    return False, f"JWT Token已过期 (过期时间: {exp_time.strftime('%Y-%m-%d %H:%M:%S')})"
                return True, ""
            except Exception as e:
                return False, f"JWT Token格式无效: {e}"
        
        return False, "未识别的Token格式，请提供API Key (sk-) 或JWT Token"
    
    def is_token_available(self) -> bool:
        """检查是否有可用的Token"""
        token = self.get_token()
        return token is not None and not self._is_token_expired()