from pathlib import Path

from dotenv import load_dotenv

from src.core.conf import settings
from src.core.register import register_app

load_dotenv()

app = register_app()

if __name__ == '__main__':
    # 如果你喜欢在 IDE 中进行 DEBUGmain 启动方法会很有帮助
    # 如果你喜欢通过 print 方式进行调试，建议使用 fastapi cli 方式启动服务
    import uvicorn
    try:
        config = uvicorn.Config(
            app=f'{Path(__file__).stem}:app',
            reload=settings.APP_DEBUG,
            port=settings.APP_PORT,
            host=settings.APP_HOST,
            log_config=None
        )
        config.setup_event_loop()
        server = uvicorn.Server(config)
        server.run()
    except Exception:
        raise
