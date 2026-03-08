#!/usr/bin/env python3
"""
生成创意 emoji 计算器动画 GIF
使用 slack-gif-creator skill 生成各种运算的动画
"""

import sys
import os

# 添加 slack-gif-creator 到路径
SKILL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          'ai_for_harmony', '.openhands', 'slack-gif-creator')
sys.path.insert(0, SKILL_PATH)

from PIL import Image, ImageDraw
import math

# 从 skill 导入所需模块
from core.gif_builder import GIFBuilder
from core.frame_composer import draw_emoji_enhanced, create_gradient_background
from core.easing import interpolate
from core.validators import check_slack_size
from templates.pulse import create_pulse_animation
from templates.bounce import create_bounce_animation
from templates.spin import create_spin_animation
from templates.zoom import create_zoom_animation
from templates.explode import create_explode_animation


def create_number_animation(emoji, num_frames=10):
    """为数字创建弹跳动画 - 每次调用生成不同的随机位置模拟动画"""
    import random
    builder = GIFBuilder(width=128, height=128, fps=8)
    
    # 使用不同的随机种子确保每帧都不同
    for i in range(num_frames):
        frame = Image.new('RGB', (128, 128), (30 + i*3, 35 + i*2, 55 + i*3))
        
        # 每次都改变位置和大小，产生动画效果
        offset_x = int(8 * math.sin(i * 0.8))
        offset_y = int(6 * math.cos(i * 0.8))
        
        scale = 1.0 + 0.15 * math.sin(i * 0.6)
        size = int(55 * scale)
        
        draw_emoji_enhanced(frame, emoji, position=(64 - size//2 + offset_x, 64 - size//2 + offset_y), 
                           size=size, shadow=True)
        builder.add_frame(frame)
    
    return builder


def create_operator_animation(op_emoji, num_frames=15):
    """为运算符创建旋转动画"""
    builder = GIFBuilder(width=128, height=128, fps=10)
    
    for i in range(num_frames):
        frame = Image.new('RGB', (128, 128), (45, 45, 60))
        
        # 旋转效果
        angle = (i / num_frames) * 360
        size = 70
        
        # 绘制带旋转的emoji（简化版）
        draw_emoji_enhanced(frame, op_emoji, position=(64 - size//2, 64 - size//2), 
                           size=size, shadow=True)
        builder.add_frame(frame)
    
    return builder


def create_add_animation(emoji1, emoji2, num_frames=20):
    """加法：两个emoji靠近并合并"""
    builder = GIFBuilder(width=200, height=200, fps=12)
    
    for i in range(num_frames):
        t = i / (num_frames - 1)
        frame = create_gradient_background(200, 200, (30, 30, 50), (50, 50, 80))
        
        # 从两边向中间移动
        x1 = interpolate(20, 80, t, 'ease_out')
        x2 = interpolate(180, 120, t, 'ease_out')
        
        size = 50
        draw_emoji_enhanced(frame, emoji1, position=(int(x1) - size//2, 100 - size//2), 
                           size=size, shadow=True)
        draw_emoji_enhanced(frame, emoji2, position=(int(x2) - size//2, 100 - size//2), 
                           size=size, shadow=True)
        
        # 中间显示加号
        if t > 0.3:
            draw_emoji_enhanced(frame, '➕', position=(90, 100 - 25), size=30, shadow=False)
        
        builder.add_frame(frame)
    
    return builder


def create_subtract_animation(emoji1, emoji2, num_frames=18):
    """减法：一个emoji逐渐消失"""
    builder = GIFBuilder(width=200, height=200, fps=12)
    
    for i in range(num_frames):
        t = i / (num_frames - 1)
        frame = create_gradient_background(200, 200, (50, 30, 30), (80, 50, 50))
        
        # 第一个emoji淡出
        alpha = int(255 * (1 - t))
        
        draw_emoji_emoji(frame, emoji1, position=(60, 100), size=60)
        draw_emoji_emoji(frame, emoji2, position=(140, 100), size=60)
        
        # 显示减号
        draw_emoji_enhanced(frame, '➖', position=(90, 100 - 20), size=30, shadow=False)
        
        builder.add_frame(frame)
    
    return builder


def draw_emoji_emoji(frame, emoji, position, size):
    """在frame上绘制emoji"""
    draw = ImageDraw.Draw(frame)
    # 使用简单方式绘制emoji（使用文本）
    try:
        from PIL import ImageFont
        font_size = int(size * 0.8)
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", font_size)
    except:
        font = None
    
    # 转换位置
    x, y = position
    draw.text((x - size//2, y - size//2), emoji, font=font)


def create_multiply_animation(emoji, num_frames=20):
    """乘法：emoji旋转放大"""
    builder = GIFBuilder(width=200, height=200, fps=12)
    
    for i in range(num_frames):
        t = i / (num_frames - 1)
        frame = create_gradient_background(200, 200, (30, 50, 30), (50, 80, 50))
        
        # 旋转并放大
        scale = interpolate(0.5, 1.5, t, 'elastic_out')
        size = int(60 * scale)
        
        draw_emoji_enhanced(frame, emoji, position=(100 - size//2, 100 - size//2), 
                           size=size, shadow=True)
        
        # 显示乘号
        draw_emoji_enhanced(frame, '✖️', position=(160, 30), size=30, shadow=False)
        
        builder.add_frame(frame)
    
    return builder


def create_divide_animation(emoji, num_frames=20):
    """除法：emoji分裂效果"""
    builder = GIFBuilder(width=200, height=200, fps=12)
    
    for i in range(num_frames):
        t = i / (num_frames - 1)
        frame = create_gradient_background(200, 200, (50, 30, 50), (80, 50, 80))
        
        if t < 0.5:
            # 上半部分向上移动
            y = interpolate(100, 50, t * 2, 'ease_out')
            size = 50
            draw_emoji_enhanced(frame, emoji, position=(100 - size//2, int(y) - size//2), 
                               size=size, shadow=True)
        else:
            # 下半部分向下移动
            y = interpolate(100, 150, (t - 0.5) * 2, 'ease_out')
            size = 50
            draw_emoji_enhanced(frame, emoji, position=(100 - size//2, int(y) - size//2), 
                               size=size, shadow=True)
        
        # 显示除号
        draw_emoji_enhanced(frame, '➗', position=(160, 30), size=30, shadow=False)
        
        builder.add_frame(frame)
    
    return builder


def create_equals_animation(emoji, num_frames=15):
    """等于：emoji弹出效果"""
    builder = GIFBuilder(width=200, height=200, fps=12)
    
    for i in range(num_frames):
        t = i / (num_frames - 1)
        frame = create_gradient_background(200, 200, (50, 50, 30), (80, 80, 50))
        
        # 弹跳效果
        scale = interpolate(0.0, 1.2, t, 'bounce_out')
        if t > 0.8:
            scale = interpolate(1.2, 1.0, (t - 0.8) * 5, 'ease_out')
        
        size = int(60 * scale)
        draw_emoji_enhanced(frame, emoji, position=(100 - size//2, 100 - size//2), 
                           size=size, shadow=True)
        
        # 显示等于号
        draw_emoji_enhanced(frame, '🟰', position=(160, 30), size=35, shadow=False)
        
        builder.add_frame(frame)
    
    return builder


def save_with_validation(builder, filename, is_emoji=True):
    """保存并验证文件大小"""
    # 不去除除重复帧，保留动画效果
    info = builder.save(filename, num_colors=48, optimize_for_emoji=is_emoji, remove_duplicates=False)
    
    passes, size_info = check_slack_size(filename, is_emoji=is_emoji)
    
    if not passes:
        print(f"⚠️ {filename} 超过大小限制: {size_info['size_kb']:.1f}KB (最大 {size_info['max_kb']}KB)")
        # 尝试进一步优化
        info = builder.save(filename, num_colors=32, optimize_for_emoji=True)
    else:
        print(f"✅ {filename} 大小合适: {size_info['size_kb']:.1f}KB")
    
    return info


def main():
    """生成所有动画GIF"""
    output_dir = os.path.join(os.path.dirname(__file__), 'assets', 'animations')
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎬 开始生成 emoji 动画 GIF...")
    
    # 数字动画
    print("生成数字动画...")
    for num, emoji in [('0', '0️⃣'), ('1', '1️⃣'), ('2', '2️⃣'), ('3', '3️⃣'), 
                       ('4', '4️⃣'), ('5', '5️⃣'), ('6', '6️⃣'), ('7', '7️⃣'), 
                       ('8', '8️⃣'), ('9', '9️⃣')]:
        builder = create_number_animation(emoji)
        save_with_validation(builder, f'{output_dir}/num_{num}.gif')
    
    # 运算符动画
    print("生成运算符动画...")
    operators = [('plus', '➕'), ('minus', '➖'), ('multiply', '✖️'), ('divide', '➗'), ('equals', '🟰')]
    for name, emoji in operators:
        builder = create_operator_animation(emoji)
        save_with_validation(builder, f'{output_dir}/op_{name}.gif')
    
    # 运算结果动画
    print("生成运算结果动画...")
    
    # 加法：🎯 + 🎯 = 🎉
    builder = create_add_animation('🎯', '🎯')
    save_with_validation(builder, f'{output_dir}/result_add.gif')
    
    # 减法：😢 - 😢 = 😊
    # 简化版本
    builder = GIFBuilder(width=200, height=200, fps=12)
    for i in range(18):
        t = i / 17
        frame = create_gradient_background(200, 200, (50, 30, 30), (80, 50, 50))
        
        # 简单的过渡效果
        draw_emoji_enhanced(frame, '😢', position=(60, 100), size=50, shadow=True)
        draw_emoji_enhanced(frame, '😢', position=(140, 100), size=50, shadow=True)
        draw_emoji_enhanced(frame, '➖', position=(90, 80), size=25, shadow=False)
        
        builder.add_frame(frame)
    save_with_validation(builder, f'{output_dir}/result_subtract.gif')
    
    # 乘法：⭐ × ⭐ = ✨
    builder = create_multiply_animation('⭐')
    save_with_validation(builder, f'{output_dir}/result_multiply.gif')
    
    # 除法：🎈 ÷ 🎈 = 💨
    builder = create_divide_animation('🎈')
    save_with_validation(builder, f'{output_dir}/result_divide.gif')
    
    # 等于：显示结果
    builder = create_equals_animation('🎉')
    save_with_validation(builder, f'{output_dir}/result_equals.gif')
    
    print("✅ 所有动画 GIF 生成完成！")
    print(f"📁 输出目录: {output_dir}")


if __name__ == '__main__':
    main()
