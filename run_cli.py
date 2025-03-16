CAPTCHA_SOLVER = True
try:
    from vk_captcha import VkCaptchaSolver
    CAPTCHA_SOLVER = True
except ImportError:
    CAPTCHA_SOLVER = False

def main():


    ...

if __name__ == '__main__':
    main()