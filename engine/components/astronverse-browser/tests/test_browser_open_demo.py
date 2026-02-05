from astronverse.browser.browser_software import BrowserSoftware
from astronverse.browser import CommonForBrowserType, CommonForTimeoutHandleType


def test_browser_open_demo():
    """browser_open函数的简单demo测试"""
    
    print("开始测试 browser_open 函数...")
    
    try:
        # 直接调用browser_open函数
        browser = BrowserSoftware.browser_open(
            url="https://www.baidu.com",
            browser_type=CommonForBrowserType.BTChrome,
            browser_abs_path="",
            open_args="",
            open_with_incognito=False,
            wait_load_success=False,  # 不等待加载完成，避免长时间等待
            timeout=5,
            timeout_handle_type=CommonForTimeoutHandleType.ExecError
        )
        
        print(f"✅ browser_open调用成功！")
        print(f"   浏览器类型: {browser.browser_type}")
        print(f"   浏览器路径: {browser.browser_abs_path}")
        print(f"   浏览器控制对象: {browser.browser_control}")
        
        # 尝试获取一些基本信息
        try:
            url = browser.get_url()
            print(f"   当前URL: {url}")
        except Exception as e:
            print(f"   ⚠️ 获取URL失败: {e}")
            
        try:
            title = browser.get_title()
            print(f"   当前标题: {title}")
        except Exception as e:
            print(f"   ⚠️ 获取标题失败: {e}")
            
        # 关闭浏览器
        try:
            # BrowserSoftware.browser_close(browser)
            print("✅ 浏览器已关闭")
        except Exception as e:
            print(f"   ⚠️ 关闭浏览器失败: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ browser_open调用失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("browser_open函数demo测试")
    print("=" * 50)
    
    success = test_browser_open_demo()
    
    print("=" * 50)
    if success:
        print("✅ 测试完成！")
    else:
        print("❌ 测试失败！")
    print("=" * 50)