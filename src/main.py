from pathlib import Path

import uvicorn

from src.core.conf import settings
from src.core.register import register_app

app = register_app()

if __name__ == '__main__':
    # 如果你喜欢在 IDE 中进行 DEBUGmain 启动方法会很有帮助
    # 如果你喜欢通过 print 方式进行调试，建议使用 fastapi cli 方式启动服务
    try:
        config = uvicorn.Config(app=f'{Path(__file__).stem}:app', reload=True, port=settings.APP_PORT, host=settings.APP_HOST)
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        raise e
