import time
from requests import RequestException

def retry_request(request_func, max_retries=3, base_delay=1):
    """
    重试请求函数，使用指数退避策略。

    Args:
    request_func (callable): 发送请求的函数。
    max_retries (int): 最大重试次数。
    base_delay (int): 初始延迟时间（秒）。

    Returns:
    Response: 请求的响应对象。

    Raises:
    RequestException: 如果所有重试都失败，则抛出异常。
    """
    for attempt in range(max_retries):
        try:
            return request_func()
        except RequestException as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
    
    raise RequestException("Max retries exceeded")

