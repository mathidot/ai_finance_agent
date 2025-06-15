import os
import yaml
from pathlib import Path

class AppConfig:
    """管理应用程序配置的类"""
    _instance = None
    _config_data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        # 获取当前文件所在目录的父目录（项目根目录）
        project_root = Path(__file__).resolve().parents[2] # 假设从 src/core/app_startup.py 到项目根目录是两层
        
        # 构造 config 目录路径
        config_dir = project_root / "src" / "config"

        # 默认加载 settings.yaml
        config_file = config_dir / "config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Default config file not found: {config_file}")

        print(f"Loading base config from: {config_file}")
        with open(config_file, 'r', encoding='utf-8') as f:
            self._config_data = yaml.safe_load(f)

        # 最后，允许环境变量覆盖配置文件中的值
        self._override_with_env_vars(self._config_data)


    def _update_config_recursive(self, base_dict, override_dict):
        """递归更新字典"""
        for k, v in override_dict.items():
            if isinstance(v, dict) and k in base_dict and isinstance(base_dict[k], dict):
                base_dict[k] = self._update_config_recursive(base_dict[k], v)
            else:
                base_dict[k] = v
        return base_dict

    def _override_with_env_vars(self, config_data, prefix="APP_"):
        """用环境变量覆盖配置，例如 APP_STRATEGY_RISK_TOLERANCE"""
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # 将环境变量名转换为配置路径
                # 例如 APP_STRATEGY_RISK_TOLERANCE -> strategy.risk_tolerance
                config_path = key[len(prefix):].replace('__', '.').lower() # 使用双下划线表示嵌套
                
                # 尝试将值转换为正确的类型 (简单实现，可更复杂)
                try:
                    if value.lower() == 'true': val = True
                    elif value.lower() == 'false': val = False
                    elif value.replace('.', '', 1).isdigit(): val = float(value)
                    elif value.isdigit(): val = int(value)
                    else: val = value
                except ValueError:
                    val = value # 转换失败，保留为字符串

                self._set_config_value(config_data, config_path.split('.'), val)

    def _set_config_value(self, config_dict, path_parts, value):
        """根据路径设置字典中的值"""
        current = config_dict
        for i, part in enumerate(path_parts):
            if i == len(path_parts) - 1:
                current[part] = value
            else:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]


    def get(self, key, default=None):
        """通过点分隔符获取配置值，例如 'strategy.indicators.RSI_period'"""
        parts = key.split('.')
        current = self._config_data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default # 找不到路径
        return current

app_config = AppConfig()