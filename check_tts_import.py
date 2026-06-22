from TTS.api import TTS
import TTS
print('loaded TTS package')
print('TTS version', getattr(TTS, '__version__', 'unknown'))
print('TTS class', TTS)
try:
    import inspect
    print('signature', inspect.signature(TTS))
except Exception as e:
    print('signature error', e)
