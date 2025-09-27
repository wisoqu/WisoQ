# gpt_grok_safe.py
import g4f
import inspect
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("wisoq.gpt")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(ch)

CACHE_FILE = Path("provider_cache.json")
DEFAULT_TIMEOUT = 5
EXTENDED_TIMEOUT = 15  # увеличиваем таймаут для медленных провайдеров

BLACKLIST_SUBSTRS = (
    "Gpt3", "Gpt-3", "GPT-3",
    "Image", "Audio", "Pollinations", "Dalle", "StableDiffusion", "WeWordle"
)
WHITELIST_SUBSTRS = ("Openai", "OpenAI", "OpenAiChat", "Azure", "DeepInfra",
                     "OpenAssistant", "OpenRouter", "Grok")  # включаем Grok

def _save_cached_provider(name: str) -> None:
    try:
        CACHE_FILE.write_text(json.dumps({"provider": name}), encoding="utf-8")
        logger.info(f"Сохранён кэш провайдера: {name}")
    except Exception as e:
        logger.warning(f"Не удалось сохранить кэш провайдера: {e}")

def _load_cached_provider() -> Optional[str]:
    try:
        if CACHE_FILE.exists():
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            return data.get("provider")
    except Exception as e:
        logger.warning(f"Не удалось прочитать кэш провайдера: {e}")
    return None

def _providers_map() -> Dict[str, Any]:
    return {name: cls for name, cls in inspect.getmembers(g4f.Provider) if inspect.isclass(cls)}

async def _try_provider_async(provider_cls, messages: list[dict], timeout: int) -> Optional[str]:
    try:
        response = await asyncio.wait_for(
            g4f.ChatCompletion.create_async(
                model=g4f.models.gpt_4_1,
                provider=provider_cls,
                messages=messages,
                stream=False
            ),
            timeout=timeout
        )
        if isinstance(response, str) and response.strip() and not response.startswith("[!["):
            return response.strip()
    except Exception as e:
        logger.debug(f"Провайдер {getattr(provider_cls,'__name__',str(provider_cls))} упал: {repr(e)}")
    return None

def get_response(messages: list[dict]) -> str:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    providers = _providers_map()
    if not providers:
        return "❌ Нет доступных провайдеров"

    cached_name = _load_cached_provider()
    if cached_name and cached_name in providers:
        logger.info(f"Проверка кэшированного провайдера {cached_name} с расширенным таймаутом...")
        # Пытаемся несколько раз, прежде чем сбросить
        for attempt in range(2):
            resp = loop.run_until_complete(_try_provider_async(providers[cached_name], messages, EXTENDED_TIMEOUT))
            if resp:
                return resp
            logger.warning(f"Попытка {attempt+1} для кэшированного провайдера {cached_name} не удалась")
        logger.warning(f"Кэшированный провайдер {cached_name} не отвечает. Сбрасываем кэш.")
        try: CACHE_FILE.unlink(missing_ok=True)
        except Exception: pass

    def is_blacklisted(name: str) -> bool:
        return any(b.lower() in name.lower() for b in BLACKLIST_SUBSTRS)

    # Формируем порядок: сначала whitelist (Grok + современные GPT), потом остальные
    ordered = []
    for name, cls in providers.items():
        if not is_blacklisted(name) and any(sub.lower() in name.lower() for sub in WHITELIST_SUBSTRS):
            ordered.append(cls)
    for name, cls in providers.items():
        if cls not in ordered and not is_blacklisted(name):
            ordered.append(cls)

    async def try_all_parallel():
        tasks = [asyncio.create_task(_try_provider_async(cls, messages, DEFAULT_TIMEOUT)) for cls in ordered]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for d in done:
            res = d.result()
            if res:
                _save_cached_provider(ordered[tasks.index(d)].__name__)
                for t in pending: t.cancel()
                return res
        # Если ничего не завершилось сразу, ждем медленно
        if pending:
            try:
                done, _ = await asyncio.wait(pending, timeout=EXTENDED_TIMEOUT)
                for d in done:
                    res = d.result()
                    if res:
                        _save_cached_provider(ordered[tasks.index(d)].__name__)
                        return res
            except Exception:
                pass
        return None

    result = loop.run_until_complete(try_all_parallel())
    if result:
        return result
    return "❌ Все текстовые провайдеры недоступны"
